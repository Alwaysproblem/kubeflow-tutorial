FROM prom/prometheus

COPY --chown=65534:65534 prome.yaml /tmp/prometheus/prome.yaml