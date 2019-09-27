FROM python:3.7

ENV PYTHONUNBUFFERED 1
ENV BILLCALLS_ENV=development
ENV BILLCALLS_SECRET_KEY="CHANGE_ME!!!! (P.S. the SECRET_KEY environment variable will be used, if set, instead)."
ENV BILLCALLS_DEBUG=true
ENV BILLCALLS_ALLOWED_HOSTS=*

RUN mkdir /code

WORKDIR /code

ADD requirements.txt /code/

RUN pip install -r requirements.txt

ADD . /code/