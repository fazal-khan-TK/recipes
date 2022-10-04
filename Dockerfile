FROM python:3.10.7-alpine3.16

LABEL maintainer="fazal-khan-tk"

ENV PYTHONUNBUFFERED 1

COPY ./app /app

COPY ./requirements.txt requirements.txt

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps build-base postgresql-dev musl-dev
RUN pip install -r requirements.txt 
RUN apk del .tmp-build-deps
RUN adduser --disabled-password --no-create-home django-user

USER django-user

WORKDIR /app

EXPOSE 8000