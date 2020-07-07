#%%
!sed -i.bak 's@%notebook-name%@vscode@g' jupyter-svc.yaml
#%%
!kubectl apply -f jupyter-svc.yaml
#%%
import sys
from random import random
from operator import add
import os
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf

#%%
os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3"
os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python3"

#%%
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
conf.set("spark.driver.host", "jupyter")
conf.set("spark.driver.port", "37371")
conf.set("spark.blockManager.port", "6060")

#%%
SparkContext(conf=conf)
spark = SparkSession.builder\
        .config(conf=conf)\
        .getOrCreate()

#%%
partitions = 100
n = 100000 * partitions

def f(_):
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0

count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
print("Pi is roughly %f" % (4.0 * count / n))

#%%
spark.stop()

# %%
os.system("kubectl delete -f jupyter-svc.yaml")
#%%
os.system("mv jupyter-svc.yaml.bak jupyter-svc.yaml")
# %%
