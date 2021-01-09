MODEL_NAME=toy

kubectl port-forward -n kubeflow-user service/${MODEL_NAME}-predictor-default-gjbvv-private 8012:80 &

curl -v --data '{"signature_name":"serving_default","inputs": [[1.0, 2.0]]}' \
  http://localhost:8012/v1/models/${MODEL_NAME}:predict

curl -v --data '{"signature_name":"serving_default","instances": [[1.0, 2.0]]}' \
  http://localhost:8012/v1/models/${MODEL_NAME}:predict
