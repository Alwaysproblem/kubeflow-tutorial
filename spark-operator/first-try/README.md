# First Try

## welcome to Toy example

- customize the jar inside docker image ([spark-tfr.dockerfile](spark-tfr.dockerfile))

    ```bash
    $ docker build -t pyspark-executor:latest -f spark-tfr.dockerfile .
    ```

- edit the mountPath and volume for your own.
- edit the image (driver, executor) for your own.
- edit the ServiceAccount  for your own.
- mind the resources for your own.
- build the docker image with `first-try.dockerfile` for your own.
- modify `mainApplicationFile` feild for your own code.
- synchronise the docker image
- run


[please use spark local default distribute file system](https://stackoverflow.com/questions/35861099/overwriting-a-spark-output-using-pyspark)