FROM python:3.6-slim-buster
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

RUN apt-get update \
        && apt-get install -y --no-install-recommends \
                curl \
                gnupg2 \
                git \
                gcc \
                python3-dev \
                build-essential \
        && apt-get autoremove -yqq --purge \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/airflow

RUN git clone \
    --filter=blob:none \
    --depth 1 \
    --single-branch \
    https://github.com/apache/airflow.git \
    /opt/airflow

ARG PIP_INSTALL_ARG
RUN pip install -U "${PIP_INSTALL_ARG}"

ARG AIRFLOW_EXTRAS
RUN AIRFLOW_VERSION=master \
    && PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)" \
    && CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
    && pip install -e ".[${AIRFLOW_EXTRAS}]"
