<!-- TODO: -->
# Components tutorial for kubeflow

## requirments

<!-- - kubeflow 0.7.1 -->
- tensorflow 2.2.0
- pytorch 1.15
- openMPI 4.0.1
- horovod 0.19
- spark 2.4.5
- kustomize 3.6.1 ([installation](https://kubernetes-sigs.github.io/kustomize/installation/))
- kfctl 1.0.2 ([installation](https://www.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/))

## installation

# kubeflow

## Requirements

- kubenetes >= 1.14
- S3FS mount to local files system （optional）

## Installation

- installation (kubeflow == 0.7.1)
  
  ```bash
  $ mkdir -p kfinstallation && cd kfinstallation
  $ cp installation/local-storage-class.yaml kfinstallation/local-storage-class.yaml
  $ kubectl apply -f local-storage-class.yaml
  $ wget https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz
  # tar -xvf kfctl_v1.0.2_<platform>.tar.gz
  $ tar -xvf kfctl_v1.0.2-0-ga476281_linux.tar.gz
  $ export PATH=$PATH:`pwd`
  # export KF_NAME=<your choice of name for the Kubeflow deployment>
  $ export KF_NAME=kfprog
  # export BASE_DIR=<path to a base directory>
  $ export BASE_DIR=`pwd`
  $ export KF_DIR=${BASE_DIR}/${KF_NAME}
  $ export CONFIG_URI=https://raw.githubusercontent.com/kubeflow/manifests/v0.7-branch/kfdef/kfctl_k8s_istio.0.7.1.yaml
  $ mkdir -p ${KF_DIR}
  $ cd ${KF_DIR}
  $ kfctl apply -V -f ${CONFIG_URI}
  ```

## Access WebUI

- ssh to remote server and start kube-proxy port-forwarding
- Use the following command to set up port forwarding to the Istio gateway.
  ```bash
  $ export NAMESPACE=istio-system
  $ kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80
  ```

- Access the central navigation dashboard at:

  ```http://localhost:8080/``` on the remote server.

- access WebUI on your own computer through ssh forwarding

  ```bash
  $ ssh -L 8008:localhost:8080 recaller-2
  # ssh -NT -L 8008:localhost:8080 recaller-2
  ```

  by doing this, you can access kubeflow with your own browser of [```http://localhost:8008```](http://localhost:8008)

<!-- TODO: need to fix local storage class -->


## tutorial

- [mpi-operator](mpi-operator/README.md)
- [pytorch-operator](pytorch-operator/README.md)
- [spark-operator](spark-operator/README.md)
- [tf-operator](tf-operator/README.mds)