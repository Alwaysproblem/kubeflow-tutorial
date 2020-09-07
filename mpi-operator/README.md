# MPI Operator

The MPI Operator makes it easy to run allreduce-style distributed training on Kubernetes. Please check out [this blog post](https://medium.com/kubeflow/introduction-to-kubeflow-mpi-operator-and-industry-adoption-296d5f2e6edc) for an introduction to MPI Operator and its industry adoption.

## Installation

- [Installation](https://github.com/kubeflow/mpi-operator/blob/master/README.md)

## Creating an MPI Job

You can create an MPI job by defining an `MPIJob` config file. See [mpi-hvd](./mpi-hvd.yaml) config file for launching a multi-node horovod training job. You may change the config file based on your requirements.

```bash
cat train.yaml
```

Deploy the `MPIJob` resource to start training:

```bash
kubectl apply -f train.yaml
```

## Monitoring an MPI Job

Once the `MPIJob` resource is created, you should now be able to see the created pods matching the specified number of GPUs. You can also monitor the job status from the status section. Here is sample output when the job is successfully completed.

```bash
kubectl get -o yaml mpijobs tensorflow-mnist
```

```yaml
apiVersion: kubeflow.org/v1alpha2
kind: MPIJob
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"kubeflow.org/v1alpha2","kind":"MPIJob","metadata":{"annotations":{},"name":"tensorflow-mnist","namespace":"default"},"spec":{"cleanPodPolicy":"Running","mpiReplicaSpecs":{"Launcher":{"replicas":1,"template":{"spec":{"containers":[{"args":["mpirun --allow-run-as-root python fashion.py"],"command":["/bin/bash","-c"],"image":"alwaysproblem/adalgohvd:latest","imagePullPolicy":"IfNotPresent","name":"mpi-launcher","resources":{"request":{"cpu":1,"memory":"6Gi"}}}]}}},"Worker":{"replicas":1,"template":{"spec":{"containers":[{"image":"alwaysproblem/adalgohvd:latest","imagePullPolicy":"IfNotPresent","name":"mpi-worker","resources":{"request":{"cpu":1,"memory":"6Gi"}}}]}}}},"slotsPerWorker":2}}
  creationTimestamp: "2020-05-15T06:05:41Z"
  generation: 1
  name: tensorflow-mnist
  namespace: default
  resourceVersion: "925589"
  selfLink: /apis/kubeflow.org/v1alpha2/namespaces/default/mpijobs/tensorflow-mnist
  uid: 1b3b1f4d-9672-11ea-9c47-fa163e79ab21
spec:
  cleanPodPolicy: Running
  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
        spec:
          containers:
          - args:
            - mpirun --allow-run-as-root python fashion.py
            command:
            - /bin/bash
            - -c
            image: alwaysproblem/adalgohvd:latest
            imagePullPolicy: IfNotPresent
            name: mpi-launcher
            resources:
              request:
                cpu: 1
                memory: 6Gi
    Worker:
      replicas: 1
      template:
        spec:
          containers:
          - image: alwaysproblem/adalgohvd:latest
            imagePullPolicy: IfNotPresent
            name: mpi-worker
            resources:
              request:
                cpu: 1
                memory: 6Gi
  slotsPerWorker: 2
status:
  completionTime: "2020-05-15T06:51:39Z"
  conditions:
  - lastTransitionTime: "2020-05-15T06:05:41Z"
    lastUpdateTime: "2020-05-15T06:05:41Z"
    message: MPIJob default/tensorflow-mnist is created.
    reason: MPIJobCreated
    status: "True"
    type: Created
  - lastTransitionTime: "2020-05-15T06:05:43Z"
    lastUpdateTime: "2020-05-15T06:05:43Z"
    message: MPIJob default/tensorflow-mnist is running.
    reason: MPIJobRunning
    status: "False"
    type: Running
  - lastTransitionTime: "2020-05-15T06:51:39Z"
    lastUpdateTime: "2020-05-15T06:51:39Z"
    message: MPIJob default/tensorflow-mnist successfully completed.
    reason: MPIJobSucceeded
    status: "True"
    type: Succeeded
  replicaStatuses:
    Launcher:
      succeeded: 1
    Worker: {}
  startTime: "2020-05-15T06:05:41Z"
```

Training should run for 100 steps and takes a few minutes on a GPU cluster. You can inspect the logs to see the training progress. When the job starts, access the logs from the `launcher` pod:

```bash
PODNAME=$(kubectl get pods -l mpi_job_name=tensorflow-mnist,mpi_role_type=launcher -o name)
```

```bash
kubectl logs -f ${PODNAME}
```

or

```bash
kubectl attach ${PODNAME}
```

## API

