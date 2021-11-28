# Python base
# ############################################################
FROM arm32v7/python:3.8-buster as python-base

COPY ./requirements.txt .

RUN pip install -U pip && \
    pip install -r requirements.txt

COPY entrypoint.sh /rpi-lights-controller/monitor/
COPY schedule_monitor.py /rpi-lights-controller/monitor/

WORKDIR /rpi-lights-controller/monitor

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]