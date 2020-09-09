FROM tensorflow/tensorflow

RUN python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir matplotlib \
    && python3 -m pip install --no-cache-dir sklearn

COPY model.py /
# COPY config.json /

ENTRYPOINT ["python", "/model.py"]
