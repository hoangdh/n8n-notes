FROM python:3.9.5-alpine

ENV LIBS="autoconf build-base"

RUN apk update \
    && apk add --no-cache ${LIBS} \
    && pip install --no-cache-dir --upgrade pip setuptools wheel requests Pillow moviepy flask \
    && mkdir /work \
    && apk remove ${LIBS}

WORKDIR /work
COPY run.py /work/

CMD python3 /work/run.py

