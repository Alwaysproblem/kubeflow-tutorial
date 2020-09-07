FROM alwaysproblem/pyspark-jupyter-notebook-k8s:v2.4.5

COPY aws-java-sdk-1.7.4.jar /opt/spark/jars
COPY hadoop-aws-2.7.3.jar /opt/spark/jars