#!/bin/bash

set -eu

# temporary for debugging
set -x

BASE_DIR=$(pwd)

TEARDOWN=true
BUILD=true
RESET=true
SHOW_LOGS=true
WAITFORDB=true

mkdir -p tests/e2e/temp
cd tests/e2e/temp

export COMPOSE_FILE="${BASE_DIR}/docker-compose.yml:$BASE_DIR/tests/e2e/docker-compose.yml"
export COMPOSE_ENV_FILES="$(pwd)/.env"

# Make sure to clean up in case of failures
finish() {
    if [ $SHOW_LOGS = true ]; then
        docker compose logs
    fi

    if [ $TEARDOWN = true ]; then
        docker compose down --volumes
    fi
}

handleError() {
    finish
    exit 1
}
trap handleError ERR


# Prepare environment
cp "${BASE_DIR}/.env-example" .env
sed -i -E 's/^DOMAIN=.*/DOMAIN=terrarun/g' .env
sed -i -E 's#^BASE_URL=.*#BASE_URL=https://terrarun#g' .env

# Just in case of leftovers from previous run.
if [ $RESET = true ]; then
    docker compose down --volumes
fi

# Rebuild containers
if [ $BUILD = true ]; then
    BUILDKIT_PROGRESS=plain docker compose build
fi

# Startup base containers for setup
docker compose up -d traefik api db minio createbucket

# @TODO Replace with a proper wait for DB.
if [ $WAITFORDB = true ]; then
    sleep 10
fi

docker compose exec -ti api alembic upgrade head

# @TODO Replace with curl or something.
TFE_TOKEN=$(docker compose exec -e PYTHONPATH=/app: -ti api python tests/e2e/scripts/bootstrap_admin.py)
export TFC_AGENT_TOKEN=$(docker compose exec -e PYTHONPATH=/app: -ti api python tests/e2e/scripts/bootstrap_agent_pool.py)

# Bring up remaining containers
docker compose up -d

docker compose exec test-runner /tests/scripts/login.sh "$TFE_TOKEN"

timeout --signal=TERM --foreground 1m docker compose exec -i -w /tests/terraform/setup test-runner sh -c "terraform init && terraform apply -auto-approve -var tfe_token='${TFE_TOKEN}' || true"

# Run terraform executing test
timeout --signal=TERM --foreground 1m docker compose exec -i -w /tests/terraform/execution test-runner terraform init
timeout --signal=TERM --foreground 3m docker compose exec -i -w /tests/terraform/execution test-runner terraform test

# Run tfe provider compatibility tests
timeout --signal=TERM --foreground 1m docker compose exec -i -w /tests/terraform/tfe_provider test-runner terraform init
timeout --signal=TERM --foreground 3m docker compose exec -i -w /tests/terraform/tfe_provider test-runner terraform test -var tfe_token="${TFE_TOKEN}"

# Teardown stack
finish
