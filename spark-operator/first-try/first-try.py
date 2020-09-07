# #%%
# import argparse
# import glob
# import json
# import os
# import time

# import pyspark as spark
# import pyspark.sql.functions as F
# from pyspark.sql import DataFrame, Row, SparkSession
# from pyspark.sql.types import IntegerType, LongType, StringType, StructField

# #%%
# def main(sparse_f, varlen_f, varlen_maxlen_f,
#         raw_train_path = "../rawDatasets/train",
#         raw_valid_path = "../rawDatasets/valid",
#         tf_train_path = "../tfRecords/train",
#         tf_valid_path = "../tfRecords/valid",
#         repartition_num_train = 20,
#         repartition_num_valid = 20,
#         time_consumption = False,
#         sep = '/'
#     ):

#     raw_train_path = str(raw_train_path) 
#     raw_valid_path = str(raw_valid_path) 

#     tf_train_path = str(tf_train_path),
#     tf_valid_path = str(tf_valid_path),

#     dic_base = raw_train_path.split(os.sep)
#     dic_base.pop()
#     dic_base = sep.join(dic_base)

#     sparse_dic_path = dic_base + sep + "sparse_dic.json"
#     varlen_dic_path = dic_base + sep + "varlen_dic.json"

#     config_path = dic_base + sep + "config.json"

#     conf = spark.SparkConf()
#     sparkv = SparkSession.builder \
#              .config(conf=conf) \
#              .appName("SparkTF") \
#              .getOrCreate()
#     sc = sparkv.sparkContext

#     def stripD(k):
#         k = k.strip().split("|")
#         target = int(k[0].strip()[-1])
#         k.pop(0)
#         k = list(map(int, k[0].strip().split()))
#         g = {idd: '0' for idd in sparse_f}
#         g_v = {idd: ['0'] for idd in varlen_f}
#         g.update(g_v)
#         for aas in k:
#             try:
#                 if f"f{aas >> 54}" in sparse_f:
#                     g[f"f{aas >> 54}"] = str(aas & 0x003fffffffffffff)
#                 elif f"f{aas >> 54}" in varlen_f:
#                     g[f"f{aas >> 54}"].append(str(aas & 0x003fffffffffffff))
#                 else:
#                     pass
#             except KeyError:
#                 pass

#         for i in g:
#             if isinstance(g[i], list) and len(g[i]) > 1:
#                 g[i].pop(0)
#         return g, target

#     rddt = sc.textFile(raw_train_path + sep + "*").map(stripD).map(lambda x: Row(**x[0], label=x[1]))
#     rddv = sc.textFile(raw_valid_path + sep + "*").map(stripD).map(lambda x: Row(**x[0], label=x[1]))

#     dkeyt = list(rddt.take(1)[0].asDict().keys())
#     dft = rddt.toDF(dkeyt)
#     dkeyv = list(rddv.take(1)[0].asDict().keys())
#     dfv = rddv.toDF(dkeyv)

#     df = dft.union(dfv)


#     print("start counting\n")
#     s = time.time()
#     len_valid = dfv.count()
#     len_train = dft.count()
#     e = time.time()
#     print("done.\n")
#     if time_consumption:
#         print(f"the duration of this part is {(e - s) * 1000}ms.")

#     df.createOrReplaceTempView("tmp")
#     dfspa = sparkv.sql(f"select {', '.join(['f' + str(i) for i in sparse])} from tmp")
#     dfvar = sparkv.sql(f"select {', '.join(['f' + str(i) for i in varlen])} from tmp")
#     sparkv.catalog.dropTempView("tmp")

#     print("aggerating the sparse parameter.\n")
#     s = time.time()
#     kfdic = {}
#     for kf in sparse:
#         temp = dfspa\
#                 .select(f"f{kf}")\
#                 .distinct()\
#                 .orderBy(F.col(f"f{kf}"))\
#                 .rdd.zipWithIndex()\
#                 .map(lambda row: tuple(row[0]) + (row[1] + 1, ))\
#                 .collectAsMap()

#         if "0" in temp:
#             temp.pop("0")
#             for k in temp:
#                 temp[k] -= 1
#         temp.update({'0': 0})

#         kfdic[f"f{kf}"] = temp

#     # kfdic
#     try:
#         with open(sparse_dic_path, "w") as logdic:
#             json.dump(kfdic, logdic)
#     except:
#         print("Fail to writing sparse dictionary to file....\n")

#     e = time.time()
#     print("done.\n")

#     if time_consumption:
#         print(f"the duration of this part is {(e - s) * 1000}ms.\n")

#     print("aggregating the varlen parameter.\n")
#     s = time.time()
#     kfvdic = {}
#     for kf in varlen:
#         temp = dfvar\
#             .select(F.explode(f"f{kf}").alias('zz'))\
#             .distinct()\
#             .orderBy(F.col("zz"))\
#             .rdd.zipWithIndex()\
#             .map(lambda row: tuple(row[0]) + (row[1] + 1, ))\
#             .collectAsMap()
        
#         if "0" in temp:
#             temp.pop("0")
#             for k in temp:
#                 temp[k] -= 1

#         temp.update({'0': 0})

#         kfvdic[f"f{kf}"] = temp
#     # kfvdic
#     try:
#         with open(varlen_dic_path, "w") as logdic:
#             json.dump(kfvdic, logdic)
#     except:
#         print("Fail to writing sparse dictionary to file....\n")
#     e = time.time()
#     print("done.\n")
#     if time_consumption:
#         print(f"the duration of this part is {(e - s) * 1000}ms.\n")

#     print("parsing the parameter dictionary...\n")
#     s = time.time()
#     chkenc_v = {}
#     for kfv in kfvdic:
#         chkenc_v[kfv] = max([int(kfvdic[kfv][i]) for i in kfvdic[kfv]])
#     print(chkenc_v)
#     varlen_config_dic = chkenc_v.copy()
#     chkenc_s = {}
#     for kf in kfdic:
#         chkenc_s[kf] = max([int(kfdic[kf][i]) for i in kfdic[kf]])
#     print(chkenc_s)
#     sparse_config_dic = chkenc_s.copy()
#     e = time.time()
#     print("done.\n")
#     if time_consumption:
#         print(f"the duration of this part is {(e - s) * 1000}ms.\n")

#     dfks_train = dft
#     dfks_valid = dfv

#     def parse(x):
#         x = x.asDict()
#         for kk in x:
#             if kk in sparse_f:
#                 x[kk] = kfdic[kk][x[kk]]
#             elif kk in varlen_f:
#                 temp = kfvdic[kk]
#                 for ind, val in enumerate(x[kk]):
#                     x[kk][ind] = temp[val]
#                 if len(x[kk]) != varlen_maxlen_f[kk]:
#                     x[kk] += [0 for _ in range(0, varlen_maxlen_f[kk] - len(x[kk]))]
#         return x


#     print("transforming the raw data.\n")
#     s = time.time()
#     rdd_t = dfks_train.rdd.map(parse).map(lambda x: Row(**x))
#     dkeyt = list(rdd_t.take(1)[0].asDict().keys())
#     dftrain = rdd_t.toDF(dkeyt)

#     rdd_v = dfks_valid.rdd.map(parse).map(lambda x: Row(**x))
#     dkeyv = list(rdd_v.take(1)[0].asDict().keys())
#     dfvalid = rdd_v.toDF(dkeyv)

#     df3 = dftrain.union(dfvalid)
#     e = time.time()
#     print("done.\n")
#     if time_consumption:
#         print(f"the duration of this part is {(e - s) * 1000}ms.\n")

#     print("writing the processed data to files.\n")

#     with open(config_path, "w+") as f:
#         json.dump((sparse_config_dic, varlen_config_dic, varlen_maxlen_f, len_train, len_valid), f)


#     dftrain.repartition(repartition_num_train)\
#         .write \
#         .format("tfrecords") \
#         .option("recordType", "Example")\
#         .mode("overwrite") \
#         .save(tf_train_path)
#     #%%
#     dfvalid.repartition(repartition_num_valid)\
#         .write \
#         .format("tfrecords") \
#         .option("recordType", "Example")\
#         .mode("overwrite") \
#         .save(tf_valid_path)
#     #%%
#     print("done.\n")
#     #%%
#     print("clean those useless files.")
#     for ff in glob.glob(f"{tf_train_path}/*"):
#         if "part" in ff:
#             os.rename(ff, ff + ".tfrecords")

#     for cleanup in glob.glob(f"{tf_train_path}/*") + glob.glob(f"{tf_train_path}/.*"):
#         # print(cleanup)
#         if not cleanup.endswith(".tfrecords"):
#             os.remove(cleanup)

#     for ff in glob.glob(f"{tf_valid_path}/*"):
#         if "part" in ff:
#             os.rename(ff, ff + ".tfrecords")

#     for cleanup in glob.glob(f"{tf_valid_path}/*") + glob.glob(f"{tf_valid_path}/.*"):
#         # print(cleanup)
#         if not cleanup.endswith(".tfrecords"):
#             os.remove(cleanup)

#     df3.show()
#     print("well done, you can train whatever you want.")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='submit')
#     parser.add_argument('--RD-train-path', "-rt",
#             type=str, action='store', help='the path of input training file',
#             dest="RD_train_path", default= "../rawDatasets/train")
#     parser.add_argument('--RD-valid-path', "-rv",
#             type=str, action='store', help='the path of input validation file',
#             dest="RD_valid_path",  default="../rawDatasets/valid")
#     parser.add_argument('--TF-train-path', "-tt",
#             type=str, action='store', help='the path of training input file',
#             dest="TF_train_path", default="../tfRecords/train")
#     parser.add_argument('--TF-valid-path', "-tv",
#             type=str, action='store', help='the path of validation input file',
#             dest="TF_valid_path", default="../tfRecords/valid")
#     parser.add_argument('--TF-train-num', "-ttn",
#             type=int, action='store', help='the path of validation input file',
#             dest="TF_train_num", default=20)
#     parser.add_argument('--TF-valid-num', "-tvn",
#             type=int, action='store', help='the path of validation input file',
#             dest="TF_valid_num", default=20)

#     args = parser.parse_args()

#     sparse = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
#                 58, 59, 60, 61, 62, 64, 68, 69, 77, 81, 82, 83, 84, 85, 86, 87,
#                 90, 92, 98, 100, 101, 102, 103, 104, 151, 152, 160,
#                 161, 162, 163, 164, 166, 167, 251]

#     varlen = [51, 52, 53, 54, 55, 56, 57, 63, 65, 66, 67, 71, 72, 73, 
#                 74, 75, 76, 88, 89, 91, 93, 94, 95, 96, 97, 99, 153,
#                 154, 155, 156, 157, 158, 159, 165]

#     varlen_maxlen = [10, 5, 5, 5, 5, 30, 60, 30, 3, 5, 10, 1, 2, 2, 2, 
#                         5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
#                         3, 2] 

#     sparse_f = [f"f{i}" for i in sparse]
#     varlen_f = [f"f{i}" for i in varlen]
#     varlen_maxlen_f = {f"f{i}": j for i, j in zip(varlen, varlen_maxlen)}
#     main( 
#         sparse_f, varlen_f, varlen_maxlen_f,
#         raw_train_path = args.RD_train_path,
#         raw_valid_path = args.RD_valid_path,
#         tf_train_path = args.TF_train_path,
#         tf_valid_path = args.TF_valid_path,
#         repartition_num_train = args.TF_train_num,
#         repartition_num_valid = args.TF_valid_num,
#         time_consumption=True
#         )


#%%
import pyspark as spark
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StringType, StructField, IntegerType, LongType
import pyspark.sql.functions as F
import argparse
import sys
import time
import os

#%%
def parse(x):
    n, c = x.strip().split(',')
    return Row(c1 = int(n), c2 = c.strip())

RD_path = '/test/dataset/data.txt'
TF_path = 'file:///test/output' # this is using the local file system of spark default distribute file system
# TF_path = '/test/output'

conf = spark.SparkConf()
sparkv = SparkSession.builder \
            .config(conf=conf) \
            .getOrCreate()

sc = sparkv.sparkContext
rddx = sc.textFile(RD_path).map(parse)
print(sys.version)
# time.sleep(3600)
print(f"the collection is {rddx.collect()}")
df = rddx.toDF(['c1', 'c2'])
#%%
df.show()

#%%
df.write\
    .format("tfrecords")\
    .option("recordType", "Example")\
    .mode("overwrite")\
    .save(TF_path)