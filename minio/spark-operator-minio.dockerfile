FROM alwaysproblem/pyspark-operator-k8s:v2.4.5-minio

COPY spark-test.py /opt/spark/work-dir/