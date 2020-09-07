# minio setup and test

## minio server local test (on mac)

1. install spark
2. start minio server with docker, create a databrick and upload file `aa.txt`

   ```bash
   $ docker run --rm -ti -e "MINIO_ACCESS_KEY=minio" -e "MINIO_SECRET_KEY=minio123" -p 9000:9000 minio/minio server /data
    # Endpoint:  http://172.17.0.2:9000 (this is for other docker)  http://127.0.0.1:9000 (this is for computer outside docker)
    # AccessKey: minio
    # SecretKey: minio123

    # Browser Access:
    # http://172.17.0.2:9000  http://127.0.0.1:9000

    # Command-line Access: https://docs.min.io/docs/minio-client-quickstart-guide
    # $ mc config host add myminio http://172.17.0.2:9000 minio minio123

    # Object API (Amazon S3 compatible):
    # Go:         https://docs.min.io/docs/golang-client-quickstart-guide
    # Java:       https://docs.min.io/docs/java-client-quickstart-guide
    # Python:     https://docs.min.io/docs/python-client-quickstart-guide
    # JavaScript: https://docs.min.io/docs/javascript-client-quickstart-guide
    # .NET:       https://docs.min.io/docs/dotnet-client-quickstart-guide
   ```

3. Download [hadoop-aws-2.7.3.jar](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/2.7.3) and [aws-java-sdk-1.7.4.jar](https://mvnrepository.com/artifact/com.amazonaws/aws-java-sdk/1.7.4) and copy to `$SPARK_HOME/jars` (**mind the version**)
4. Initiate the `pyspark` where `10.249.252.88` is from `en0` instead of `localhost` or `127.0.0.1`

    ```bash
    $ pyspark \
    --jars aws-java-sdk-1.7.4.jar,hadoop-aws-2.7.3.jar \
    --conf spark.hadoop.fs.s3a.endpoint=http://10.249.252.88:9000 \
    --conf spark.hadoop.fs.s3a.access.key=minio \
    --conf spark.hadoop.fs.s3a.secret.key=minio123 \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
    ```

5. test it

    ```python
    >>> df = spark.read.csv("s3a://data/aa.txt")
    >>> df.show()
    +---+---+---+
    |_c0|_c1|_c2|
    +---+---+---+
    |  1|  2|  3|
    |  2|  3|  4|
    |  4|  5|  6|
    |  5|  6|  7|
    +---+---+---+

    >>> df.write.csv("s3a://data/out")
    >>> 
    ```

<!-- https://github.com/AICoE/tf-serving-in-container -->

## minio gateway on k8s

1. start gateway service

    ```bash
    $ cd minio
    $ kubectl apply -f deploy/
    ```

    - remember the dns `service-name.namespace-name.svc.cluster.local`
    so the endpoint is `minio-service.minio-gateway.svc.cluster.local:9000`

2. minio client test

    ```bash
    $ kubectl run test --image=minio/mc --command -- /bin/sh -c "sleep 1d"
    $ kubectl exec -ti pod/test-6fbdf9b8c9-v2fvl -- sh # find pod-name with `kubectl get all`
    / # mc config host add mys3 http://minio-service.minio-gateway.svc.cluster.local:9000 <access_key> <secret_key>
    / # mc ls mys3
    ```

3. Tensorflow env

    ```bash
    export AWS_ACCESS_KEY_ID=<access_key>
    export AWS_SECRET_ACCESS_KEY=<secret_key>
    export AWS_REGION=us-east-1
    export S3_USE_HTTPS=0
    export S3_VERIFY_SSL=0
    export S3_ENDPOINT=minio-service.minio-gateway.svc.cluster.local:9000
    ```

4. jupyter spark test
    - dockerfile [driver-jupyter](./spark-minio.dockerfile) and [executor](./spark-minio-exec.dockerfile)
    - note that the spark config need to be set

    ```python
    conf.set("spark.hadoop.fs.s3a.endpoint", "http://minio-service.minio-gateway.svc.cluster.local:9000")
    conf.set("spark.hadoop.fs.s3a.access.key", "REPZYN3EYQTPWL8WII05")
    conf.set("spark.hadoop.fs.s3a.secret.key", "EoGTlrWZeP2IQynm4EjxFr0kQHGTxU3yp0MU1r8J")
    conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
    conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    ```

5. spark-operator test

    ```bash
    ```

## for tensorflow serving

```bash
$ docker run --rm -it -p 8500:8500 -p 8501:8501 -e "AWS_ACCESS_KEY_ID=minio" -e "AWS_SECRET_ACCESS_KEY=minio123" -e "AWS_REGION=us-east-1" -e "S3_USE_HTTPS=0" -e "S3_VERIFY_SSL=0" -e "S3_ENDPOINT=10.249.252.88:9000"  tensorflow/serving --model_config_file=s3://save/Toy.config --model_config_file_poll_wait_seconds=60
```