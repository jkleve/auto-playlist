FROM python:alpine3.15

EXPOSE 5001

# RUN apk add libxml2-dev libxslt-dev build-base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

ENV FLASK_APP=main.py
ENV FLASK_ENV=development
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5001"]
