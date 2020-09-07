#!/bin/bash
if [[ -f "train.yaml" ]]; then
    TF_JOB_NAME=$(cat train.yaml | grep -E "^  name:(.*?)" | awk '/name:/ {print $2}')
else
    TF_JOB_NAME=$1
fi

PODNAME=$(kubectl get pods -l tf-job-name=${TF_JOB_NAME},tf-replica-index=0 -o name)
kubectl attach ${PODNAME}
