FROM python:3.8-slim

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

ADD . /worker
WORKDIR /worker

ENTRYPOINT python3 worker.py