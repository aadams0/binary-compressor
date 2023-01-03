FROM python:3.8-slim

EXPOSE 5000

COPY . .
RUN pip3 install -r /requirements.txt

ADD . /flask_app
WORKDIR /flask_app

RUN pip3 install -r requirements.txt

ENV FLASK_DEBUG=true
CMD flask run --host 0.0.0.0
