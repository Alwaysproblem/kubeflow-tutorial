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

https://github.com/kubeflow/kubeflow/issues/4306

## jupyter notebook setup

- first you need to edit the configuration of namespaces (if you have istio)

  ```bash
  $ kubectl edit ns adx
  # apiVersion: v1
  # kind: Namespace
  # metadata:
  #   annotations:
  #     owner: anonymous@kubeflow.org
  #   creationTimestamp: "2020-07-03T05:44:52Z"
  #   labels:
  #     istio-injection: disabled   ----------------------------> this should be `disabled`
  #     katib-metricscollector-injection: enabled
  #     serving.kubeflow.org/inferenceservice: enabled
  #   name: adx
  #   ownerReferences:
  #   - apiVersion: kubeflow.org/v1beta1
  #     blockOwnerDeletion: true
  #     controller: true
  #     kind: Profile
  #     name: adx
  #     uid: 841605b5-032e-4f80-a59a-af0dca29108a
  #   resourceVersion: "1457566"
  #   selfLink: /api/v1/namespaces/adx
  #   uid: 99b8fcdb-f58d-4682-941f-4fce50aa645d
  # spec:
  #   finalizers:
  #   - kubernetes
  ```

- then build docker image with `dockerfile.spark`
- setup a new jupyter notebook server
- find the `oauthToken`

  ```bash
  $ kubectl describe sa default-editor -n adx
  # Name:                default-editor
  # Namespace:           adx
  # Labels:              <none>
  # Annotations:         <none>
  # Image pull secrets:  <none>
  # Mountable secrets:   default-editor-token-9vrnl
  # Tokens:              default-editor-token-9vrnl  --------------> this is what we want
  # Events:              <none>
  $ kubectl describe secret default-editor-token-9vrnl -n adx
  # Name:         default-editor-token-9vrnl
  # Namespace:    adx
  # Labels:       <none>
  # Annotations:  kubernetes.io/service-account.name: default-editor
  #               kubernetes.io/service-account.uid: dc9d9f60-4c95-4b83-ba9b-a5a066e31cf1

  # Type:  kubernetes.io/service-account-token

  # Data
  # ====
  # token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJhZHgiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoiZGVmYXVsdC1lZGl0b3ItdG9rZW4tOXZybmwiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdC1lZGl0b3IiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJkYzlkOWY2MC00Yzk1LTRiODMtYmE5Yi1hNWEwNjZlMzFjZjEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6YWR4OmRlZmF1bHQtZWRpdG9yIn0.BX-ZEMtLicSnobcxDGJu_V6SXIb6M53ax4PNsDU0sOInWhRFI6QFzJURt3o4TFfI4x0HV5TKrdI2aCPQUw2GcCRxpZDaoMaJqL7Qb89LBn_1-gWIOPzSwCz0vHUe0LoRpWAZViuJUb6Wd1GoZGTYVJ8k_JtzdNmmIj-IxVCsgTbGP_dSlJpUhQsw0twbUpXqZEB5IEg5sSew5z59JNYJHPGSMICgkPWnL4DTeUQh3W-4K_L7JStqMvUAejFti_ZssqTr7fKwoEXWKAx4OnMYnfamy4tOgtTPNnV12IXG93oiaC0M392sA_UPkNgpUhKk3XAA4sBoBWoPk55zpwA9tg ----------------------> and token is wanted.
  # ca.crt:     1025 bytes
  # namespace:  3 bytes
  ```

- code startup

  ```python
  import sys
  from random import random
  from operator import add
  
  from pyspark.sql import SparkSession
  from pyspark import SparkContext, SparkConf
  conf = SparkConf().setAppName('sparktest').setMaster('k8s://https://kubernetes.default.svc:443')
  conf.set("spark.submit.deployMode","client")
  conf.set("spark.kubernetes.namespace", "adx")
  conf.set("spark.kubernetes.authenticate.driver.serviceAccountName", "default-editor")
  conf.set("spark.kubernetes.authenticate.driver.oauthToken", "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJhZHgiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoiZGVmYXVsdC1lZGl0b3ItdG9rZW4tOXZybmwiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdC1lZGl0b3IiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJkYzlkOWY2MC00Yzk1LTRiODMtYmE5Yi1hNWEwNjZlMzFjZjEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6YWR4OmRlZmF1bHQtZWRpdG9yIn0.BX-ZEMtLicSnobcxDGJu_V6SXIb6M53ax4PNsDU0sOInWhRFI6QFzJURt3o4TFfI4x0HV5TKrdI2aCPQUw2GcCRxpZDaoMaJqL7Qb89LBn_1-gWIOPzSwCz0vHUe0LoRpWAZViuJUb6Wd1GoZGTYVJ8k_JtzdNmmIj-IxVCsgTbGP_dSlJpUhQsw0twbUpXqZEB5IEg5sSew5z59JNYJHPGSMICgkPWnL4DTeUQh3W-4K_L7JStqMvUAejFti_ZssqTr7fKwoEXWKAx4OnMYnfamy4tOgtTPNnV12IXG93oiaC0M392sA_UPkNgpUhKk3XAA4sBoBWoPk55zpwA9tg")
  conf.set("spark.kubernetes.container.image", "gcr.io/spark-operator/spark-py:v2.4.5")
  # conf.set("spark.kubernetes.allocation.batch.size", "5")
  conf.set("spark.kubernetes.executor.instances", "1")
  conf.set("spark.driver.bindAddress", "0.0.0.0")
  conf.set("spark.kubernetes.pyspark.pythonVersion", "3")
  conf.set("spark.driver.host", "spark")
  conf.set("spark.driver.port", "37371")
  conf.set("spark.blockManager.port", "6060")
  
  
  
  SparkContext(conf=conf)
  spark = SparkSession.builder\
          .config(conf=conf)\
          .getOrCreate()
  ```