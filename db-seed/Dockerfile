FROM rpi-lts-ctrl-service as python-build

USER 0

COPY requirements.txt .

RUN pip install -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY seed-db.py /rpi-lights-controller/api
COPY entrypoint.sh /rpi-lights-controller/api

WORKDIR /rpi-lights-controller/api

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
