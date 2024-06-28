FROM python:3.8.10

ARG TRACEQ_HOME="/root/.local/src/traceq"

WORKDIR ${TRACEQ_HOME}

RUN apt-get update && \
    pip install --upgrade pip

COPY . .

RUN pip install .