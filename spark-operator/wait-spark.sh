#!/bin/bash
set -ex
while [ $(kubectl get sparkapp/pyspark-pi --template={{.status.applicationState.state}}) != "COMPLETED" ]
do
   sleep 1s;
done 
