# TF2.0 MultiWorkerMirroredStrategy operator

## Installation

```bash
kfctl build -V -f https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.2.yaml
```

## Train

- modify source code with [rules](https://www.tensorflow.org/tutorials/distribute/multi_worker_with_keras)
  - Do not need the configuration of `TF_CONFIG` because the tf-operator will set up for you
  - shard the dataset
  - `batch()` from tf.data API is global batch, be careful to deal with batch size
- build your own docker
  - see the [example](Dockerfile), build from image from tensorflow
- edit [yaml file](train.yaml)
  - edit the resources, mountPath, replicas
- run!!!

## Reference

- [kubeflow/tf-operator #1164](https://github.com/kubeflow/tf-operator/pull/1164)

## Note

- please `limit` the resources or using `podAntiAffinity` to make pod spread to every node