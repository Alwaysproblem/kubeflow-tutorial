# import pyspark as spark
from pyspark import SparkConf
# import pyspark.sql.functions as F
from pyspark.sql import SparkSession


conf = SparkConf()
spark = SparkSession.builder \
            .config(conf=conf) \
            .appName("SparkTF") \
            .getOrCreate()
sc = spark.sparkContext

df = spark.read.csv("s3a://ASH-ADX01/yongxi/data/aa.txt")
df.show()

df.repartition(4).write.csv("s3a://ASH-ADX01/yongxi/data/from-spark-operator/")