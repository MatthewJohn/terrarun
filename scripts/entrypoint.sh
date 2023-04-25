#!/bin/bash

set -e
set -x

# Switch to specific terraform version
if [[ ! -z "${TERRAFORM_VERSION}" ]]
then
    tfswitch $TERRAFORM_VERSION
fi

# Check if database upgrades are to be performed
if [ "${MIGRATE_DATABASE}" == "True" ]
then
    alembic upgrade head
fi

# Check whether to upgrade database and exit
if [ "${MIGRATE_DATABASE_ONLY}" == "True" ]
then
    exit
fi

# Run main executable
python -u ./terrarun.py --ssl-cert-private-key ./bin/example/ssl/dev.key --ssl-cert-public-key ./bin/example/ssl/dev.crt
