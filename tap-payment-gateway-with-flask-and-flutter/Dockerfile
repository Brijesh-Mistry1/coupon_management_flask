FROM python:3.6

ADD . /tap-payment-gateway-with-flask-and-flutter

WORKDIR /tap-payment-gateway-with-flask-and-flutter

RUN pip install -r requirements.txt

ENV DATABASE_HOST=db

ENV FLASK_APP=__init__.py
