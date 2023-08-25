FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

RUN mkdir -p /home/app

WORKDIR /home/app

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-deps

COPY . .