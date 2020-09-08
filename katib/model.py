# %%
# from IPython.display import display
import json
import os
from datetime import datetime

import numpy as np
import tensorflow as tf
from deepctr.models import DeepFM, WDL, xDeepFM, AutoInt, DIN, DIEN, DSIN, DCN
from deepctr.feature_column import SparseFeat, VarLenSparseFeat, get_feature_names
from minio import Minio
from minio.error import ResponseError
from io import BytesIO

def minio_client():
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or None
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or None
    AWS_REGION = os.environ.get('AWS_REGION') or None
    S3_USE_HTTPS = True if os.environ.get('S3_USE_HTTPS') not in ('0', 'false', 'False') else False
    # S3_VERIFY_SSL = True if os.environ.get('S3_VERIFY_SSL') not in ('0', 'false', 'False') else False
    S3_ENDPOINT = os.environ.get('S3_ENDPOINT') or None

    if S3_ENDPOINT == None:
        raise ValueError("there is no endpoint address in variable `S3_ENDPOINT`")

    return Minio(S3_ENDPOINT, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY,
          secure=S3_USE_HTTPS, region=AWS_REGION)


# %%

def write2minio(minioClient: Minio, path: str, data: str, encoding='utf-8'):
    """
    write string to minio.
    """
    if not path.startswith("s3://") and not path.startswith("s3a://") \
            and not path.startswith("s3o://") and not path.startswith("s3n://"):
        raise ValueError("the minio path you are writing to is invalid.")
    
    objects = [*filter(len, path.split(':')[-1].split('/'))]

    data_bricks_name, object_name = objects[0], objects[1:]
    
    # Put a file with default content-type.
    try:
        content_endcoded = data.encode(encoding)
        content_bytes = BytesIO(content_endcoded)
        minioClient.put_object(data_bricks_name, 
                '/'.join(object_name), content_bytes, length=len(content_endcoded))
    except ResponseError as err:
        print(err)
        raise err

def get_object(minioClient: Minio, remote_path: str, local_path: str):
    if not remote_path.startswith("s3://") and not remote_path.startswith("s3a://") \
            and not remote_path.startswith("s3o://") and not remote_path.startswith("s3n://"):
        raise ValueError("the minio path you are writing to is invalid.")

    objects = [*filter(len, remote_path.split(':')[-1].split('/'))]

    data_bricks_name, object_name = objects[0], objects[1:]

    # Put a file with default content-type.
    try:
        minioClient.fget_object(data_bricks_name, '/'.join(object_name), local_path)
    except ResponseError as err:
        print(err)
        raise err

def put_object(minioClient: Minio, local_path: str, remote_path: str):
    if not remote_path.startswith("s3://") and not remote_path.startswith("s3a://") \
            and not remote_path.startswith("s3o://") and not remote_path.startswith("s3n://"):
        raise ValueError("the minio path you are writing to is invalid.")

    objects = [*filter(len, remote_path.split(':')[-1].split('/'))]

    data_bricks_name, object_name = objects[0], objects[1:]

    # Put a file with default content-type.
    try:
        minioClient.fput_object(data_bricks_name, '/'.join(object_name), local_path)
    except ResponseError as err:
        print(err)
        raise err

def Decode(file_paths: list, col_type: dict, target: str, batchsize: int,
            num_parallel_calls=None, buffer_size=None, block_length=1, cycle_length=None,
            sparses=[], varlens=[], numerics=[],
            globalSparsePara={}, globalVarlenPara={},
            globalNumericPara={}, omit_label = False):
        op_dic = {
                'stringv': tf.io.VarLenFeature(tf.string),
                'string': tf.io.FixedLenFeature((), tf.string),
                'int32': tf.io.FixedLenFeature((), tf.int32),
                'int64': tf.io.FixedLenFeature((), tf.int64),
                'float32': tf.io.FixedLenFeature((), tf.float32),
                'float64': tf.io.FixedLenFeature((), tf.float64),
                'int32List': tf.io.VarLenFeature(tf.int32),
                'int64List': tf.io.VarLenFeature(tf.int64),
                'float32List': tf.io.VarLenFeature(tf.float32),
                'float64List': tf.io.VarLenFeature(tf.float64),
            }
        feature_key_value_pair = {}
        for col in col_type:
            feature_key_value_pair[col] = op_dic[col_type[col]]

        def map_decoder(serialized_example):
            
            sample = tf.io.parse_example(serialized_example, feature_key_value_pair)

            if len(varlens) != 0 and len(globalVarlenPara) != 0:
                for v in varlens:
                    sample[v] = tf.sparse.to_dense(sample[v])
                    # sample[v].set_shape((tf.newaxis, globalVarlenPara[v]))
            
            y = sample.pop(target)
            if omit_label == True:
                return sample
            else:
                return (sample, y)
            # return sample
        
        files = tf.data.Dataset.list_files(file_paths)
        if cycle_length is not None:
            dataset = files.interleave(lambda x:
                            tf.data.TFRecordDataset(x)\
                                .batch(batchsize).map(map_decoder, num_parallel_calls=num_parallel_calls),
                            cycle_length=cycle_length,
                            block_length=block_length,
                            num_parallel_calls=num_parallel_calls)
        else:
            dataset = files.interleave(lambda x:
                            tf.data.TFRecordDataset(x)\
                                .batch(batchsize).map(map_decoder, num_parallel_calls=num_parallel_calls),
                            block_length=block_length,
                            num_parallel_calls=num_parallel_calls)
        return dataset

def train(NNconfig_dic,
            train_path,
            valid_path,
            version_flag_path,
            logs_base_path,
            save_path,
            serving_config_current_path,
            serving_config_new_path,
            eval_outcome_path,
            config_path,
            strategy,
            options,
            worker_index,
            num_workers,
            version):
    
    minioClient = minio_client()

    sparse = [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 
                58, 59, 60, 61, 62, 64, 68, 69, 77, 81, 82, 83, 84, 85, 86, 87,
                90, 92, 98, 100, 101, 102, 103, 104, 151, 152, 160,
                161, 162, 163, 164, 166, 167, 251]

    varlen = [51, 52, 53, 54, 55, 56, 57, 63, 65, 66, 67, 71, 72, 73, 
                74, 75, 76, 88, 89, 91, 93, 94, 95, 96, 97, 99, 153,
                154, 155, 156, 157, 158, 159, 165]

    sparse_f = [f"f{i}" for i in sparse]
    varlen_f = [f"f{i}" for i in varlen]

    col_type = {feat: "int64" for feat in sparse_f}
    col_type.update({vfeat: "int64List" for vfeat in varlen_f})
    col_type.update({'label': "int64"})

    get_object(minioClient, config_path, "config.json")
    with open("config.json") as f:
        sparse_vcab_dic, varlen_vcab_dic,\
            varlen_maxlen_f, len_train, len_valid =\
                    json.load(f)

    batchsize = NNconfig_dic["batchsize"] * num_workers
    batchsize_per_worker = NNconfig_dic["batchsize"]
    epochs = NNconfig_dic["epochs"]
    buffer_size = NNconfig_dic["buffersize"]
    num_para = tf.data.experimental.AUTOTUNE
    D_train_r = Decode(train_path,
                col_type, 
                target = 'label', 
                batchsize = batchsize,
                block_length=batchsize_per_worker,
                num_parallel_calls=num_para,
                sparses= sparse_f, 
                varlens=varlen_f,
                globalVarlenPara=varlen_maxlen_f
                )
    D_valid_r = Decode(valid_path,
                col_type, 
                target = 'label', 
                batchsize = batchsize, 
                block_length=batchsize_per_worker,
                num_parallel_calls=num_para,
                sparses= sparse_f, 
                varlens=varlen_f,
                globalVarlenPara=varlen_maxlen_f
                )
    # display(dataset)


    # %%
    if NNconfig_dic["shuffled"] == True:
        D_train = D_train_r.shuffle(buffer_size)
    else:
        pass


    D_train = D_train_r.with_options(options)
    D_valid = D_valid_r.with_options(options)

    D_train = D_train.repeat().prefetch(buffer_size=num_para)
    D_valid = D_valid.repeat().prefetch(buffer_size=num_para)

    embedding_size = NNconfig_dic["embedding_size"]

    sparse_feature_columns = [SparseFeat(feat, sparse_vcab_dic[feat] + 1, 
                                    dtype=tf.int64, embedding_dim = embedding_size) for feat in sparse_f]
    varlen_feature_columns = [VarLenSparseFeat(SparseFeat(vfeat,  
                                vocabulary_size = varlen_vcab_dic[vfeat] + 1,
                                dtype=tf.int64, embedding_dim = embedding_size), maxlen = varlen_maxlen_f[vfeat]) for vfeat in varlen_f]

    linear_feature_columns, dnn_feature_columns = \
        sparse_feature_columns + varlen_feature_columns, sparse_feature_columns + varlen_feature_columns

    with strategy.scope():
        model = DeepFM(linear_feature_columns, dnn_feature_columns,
                        dnn_hidden_units=NNconfig_dic["dnn_hidden_units"], 
                        l2_reg_dnn=NNconfig_dic["l2_reg_dnn"],
                        l2_reg_embedding=NNconfig_dic["l2_reg_embedding"],
                        l2_reg_linear=NNconfig_dic["l2_reg_linear"],
                        dnn_dropout=NNconfig_dic["dnn_dropout"],
                        dnn_use_bn=NNconfig_dic["dnn_use_bn"],
                        dnn_activation=NNconfig_dic["dnn_activation"])

        NNconfig_dic["model_name"] = "DeepFM"

        opt_dic = {
            "Adam": tf.keras.optimizers.Adam(learning_rate=NNconfig_dic["lr"]),
            "SGD": tf.keras.optimizers.SGD(learning_rate=NNconfig_dic["lr"]),
            "Adagrad": tf.keras.optimizers.Adagrad(learning_rate=NNconfig_dic["lr"]),
        }

        opt = opt_dic[NNconfig_dic["optimizer"]]

        model.compile(optimizer=opt, loss=tf.losses.BinaryCrossentropy(),
                        metrics=[tf.keras.metrics.AUC()])

    log_dir = logs_base_path + os.path.sep + NNconfig_dic["model_name"] + "_res" \
                + os.path.sep + datetime.now().strftime("%Y%m%d-%H")

    callbacks = [
        tf.keras.callbacks.TensorBoard(
            log_dir=log_dir, histogram_freq=1, profile_batch = 3),
        tf.keras.callbacks.EarlyStopping(
                monitor='val_auc', min_delta=1e-3, patience=10, verbose=1, mode='max',
                baseline=None, restore_best_weights=True
            ),
        ]

    model.fit(D_train, epochs=epochs, verbose=1 if worker_index == 0 else 0, validation_data=D_valid,
                        steps_per_epoch=max(len_train // batchsize + 1, num_workers) // num_workers , 
                        validation_steps=max(len_valid // batchsize + 1, num_workers) // num_workers,
                        callbacks = callbacks)
    
    model.save(f"""{save_path}/{NNconfig_dic["model_name"]}/{version}""")


if __name__ == "__main__":
    import argparse

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = \
                                tf.data.experimental.AutoShardPolicy.DATA

    tf_config = json.loads(os.environ.get('TF_CONFIG') or '{}')
    worker_index = tf_config['task']['index']
    num_workers = strategy.num_replicas_in_sync

    version = datetime.now().strftime('%Y%m%d')

    parser = argparse.ArgumentParser("katib example", 
                description="this is example for katib model hyperparameter search.")
    
    parser.add_argument("--batch-size", action="store", default=2048, type=int, help="batch size", dest="batch_size")
    parser.add_argument("--embedding-size", action="store", default=4, type=int, help="embedding size", dest="embedding_size")
    parser.add_argument("--lr", action="store", default=0.001, type=float, help="learning rate", dest="lr")
    parser.add_argument("--epochs", action="store", default=10, type=int, help="training epochs", dest="epochs")
    parser.add_argument("--num-layers", action="store", default=3, type=int, help="numbers of hidden layers", dest="num_layers")
    parser.add_argument("--num-hidden-unit", action="store", default=256, type=int, help="numbers of hidden units", dest="hidden_units")
    parser.add_argument("--dnn-bn", action="store", default="false", type=str, help="use batch normalization", dest="dnn_bn")
    parser.add_argument("--l2-reg-dnn", action="store", default=0., type=float, help="l2 regularization for DNN", dest="l2_reg_dnn")
    parser.add_argument("--l2-reg-embedding", action="store", default=1e-5, type=float, help="l2 regularization for embedding layer", dest="l2_reg_emb")
    parser.add_argument("--l2-reg-linear", action="store", default=1e-5, type=float, help="l2 regularization for lnear layer", dest="l2_reg_lin")
    parser.add_argument("--dnn-dropout", action="store", default=0., type=float, help="Droppout rate for DNN layer", dest="dropout")
    parser.add_argument("--dnn-activation", action="store", default="relu", type=str, help="activation function for DNN layer", dest="activation")
    parser.add_argument("--optimizer", action="store", default="Adam", type=str, help="optimizer for DN layer", dest="optimizer")

    parser.add_argument("--train-path", dest="train_path", action="store", type=str, 
                    help= "train dataset path", default= "s3://ASH-ADX01/yongxi/training/tfRecords/train/*")
    parser.add_argument("--valid-path", dest="valid_path", action="store", type=str, 
                    help= "validation dataset path", default= "s3://ASH-ADX01/yongxi/training/tfRecords/valid/*")
    parser.add_argument("--version-flag-path", dest="version_flag_path", action="store", type=str, 
                    help= "version flag file path", default= "s3://ASH-ADX01/yongxi/training/config4train/V.flag")
    parser.add_argument("--logs-base-path", dest="logs_base_path", action="store", type=str, 
                    help= "tensorboard logs path", default= "s3://ASH-ADX01/yongxi/training/logs")
    parser.add_argument("--save-path", dest="save_path", action="store", type=str, 
                    help= "model saved path", default= "s3://ASH-ADX01/yongxi/training/save")
    parser.add_argument("--serving-config-current-path", dest="serving_config_current_path", action="store", type=str, 
                    help= "current serving config path", default= "s3://ASH-ADX01/yongxi/training/serving/model_config/config/DeepFM.config")
    parser.add_argument("--serving-config-new-path", dest="serving_config_new_path", action="store", type=str, 
                    help= "serving config generated path", default= "s3://ASH-ADX01/yongxi/training/serving/model_config/config/DeepFM.bak.config")
    parser.add_argument("--eval-outcome-path", dest="eval_outcome_path", action="store", type=str, 
                    help= "evaluation outcome file output path", default= "s3://ASH-ADX01/yongxi/training/config4train/model.best")
    parser.add_argument("--config-path", dest="config_path", action="store", type=str, 
                    help= "configuration file path for training", default= "s3://ASH-ADX01/yongxi/training/config4train/config.json")


    args = parser.parse_args()

    train_path = args.train_path
    valid_path = args.valid_path
    version_flag_path = args.version_flag_path
    logs_base_path = args.logs_base_path
    save_path = args.save_path
    serving_config_current_path = args.serving_config_current_path
    serving_config_new_path = args.serving_config_new_path
    eval_outcome_path = args.eval_outcome_path
    config_path = args.config_path

    NNconfig_dic = {
        "batchsize": args.batch_size,
        "epochs": args.epochs,
        "buffersize": 4096,
        "embedding_size": args.embedding_size,
        "lr": args.lr,
        "shuffled": False,
        "dnn_hidden_units": tuple([args.hidden_units for _ in range(args.num_layers)]),
        "l2_reg_dnn": args.l2_reg_dnn,
        "l2_reg_embedding": args.l2_reg_emb,
        "l2_reg_linear": args.l2_reg_lin,
        "dnn_dropout": args.dropout,
        "dnn_use_bn": True if args.dnn_bn == "true" else False,
        "dnn_activation": args.activation,
        "optimizer": args.optimizer,
        "model_name": "DeepFM",
        # "l2_reg_cin": 0,
        # "cin_layer_size": (64, 64, 64, 64, 64),
        # "att_layer_num": 3,
        # "att_embedding_size": 8,
        # "att_head_num": 2,
        # "att_res": True,
    }

    # train()
    # print(NNconfig_dic)
    # print(train_path)
    # print(valid_path)
    # print(version_flag_path)
    # print(logs_base_path)
    # print(save_path)
    # print(serving_config_current_path)
    # print(serving_config_new_path)
    # print(eval_outcome_path)
    # print(config_path)

    train(
        NNconfig_dic=NNconfig_dic,
        train_path=train_path,
        valid_path=valid_path,
        version_flag_path=version_flag_path,
        logs_base_path=logs_base_path,
        save_path=save_path,
        serving_config_current_path=serving_config_current_path,
        serving_config_new_path=serving_config_new_path,
        eval_outcome_path=eval_outcome_path,
        config_path=config_path,
        strategy=strategy,
        options=options,
        worker_index=worker_index,
        num_workers=num_workers,
        version=version
    )

