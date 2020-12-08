#!/usr/bin/env bash

set -euox pipefail

gcloud builds submit \
    --async \
    --config=cloudbuild.yaml \
    "--substitutions=_AIRFLOW_EXTRAS=google,_PIP_INSTALL_ARG=pip @ https://github.com/uranusjr/pip/archive/new-resolver-constraint-affects-extra-entry.zip" \
    .

gcloud builds submit \
    --async \
    --config=cloudbuild.yaml \
    '--substitutions=_AIRFLOW_EXTRAS=google,_PIP_INSTALL_ARG=pip==20.2.4'\
    .
