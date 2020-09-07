FROM tensorflow/tensorflow

RUN python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir deepctr[cpu] \
    && python3 -m pip install --no-cache-dir minio

COPY model.py /
# COPY config.json /

ENTRYPOINT ["python", "/model.py"]
