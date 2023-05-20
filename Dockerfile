FROM python:3.7-alpine

LABEL maintainer = "o.cadman@live.co.uk"

ENV GROUP_ID=1000 \
    USER_ID=1000

COPY ./app /app

COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    addgroup -g ${GROUP_ID} www && \
    adduser -D -u ${USER_ID} -G www www -s /bin/sh && \
    chown www /app


USER www

EXPOSE 8000
EXPOSE 27017

ENV PATH="/py/bin:$PATH"