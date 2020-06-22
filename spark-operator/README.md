## requirement

- kustomize (>=3.6.1)
- kubenetes (>=1.14)

## installation

- download the code from [kubeflow/manifests/spark](https://github.com/kubeflow/manifests/tree/master/spark/spark-operator)

- install spark crd with kustomize tools

  ```bash
  kustomize bulid overlays/application | kubectl apply -f -
  ```

- install serviceAccount and cluster-role-bindings with [spark-operator-on-k8s](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator)
  - download [this](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/tree/master/manifest)

  ```bash
  kubectl apply -f manifest/
  ```

- test with simple example

  ```bash
  $ kubectl apply -f spark-py-pi.yaml
  # output:

  ```

## API

## Note

[original dockerfile v2.4.5](https://github.com/apache/spark/blob/branch-2.4/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/Dockerfile)

https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/api-docs.md

https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/spark-docker/Dockerfile

https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/user-guide.md