FROM python:alpine3.15
# FROM python:alpine3.15 AS builder

RUN apk add libxml2-dev libxslt-dev build-base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "main.py"]