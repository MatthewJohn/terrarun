#!/bin/bash

set -euo pipefail

# temporary for debugging
set -x

BASE_DIR=$(pwd)

TEARDOWN=false
BUILD=false
RESET=false
SHOW_LOGS=false

mkdir -p tests/e2e/temp
cd tests/e2e/temp

export COMPOSE_PROJECT_NAME=terrarun-tests
export COMPOSE_FILE="${BASE_DIR}/docker-compose.yml:$BASE_DIR/tests/e2e/docker-compose.yml"

# Make sure to clean up in case of failures
finish() {
    if [ $SHOW_LOGS = true ]; then
        docker compose logs
    fi

    if [ $TEARDOWN = true ]; then
        docker compose down --volumes
    fi
}

error() {
    finish
    exit 1
}
trap error ERR


# Prepare environment
cp "${BASE_DIR}/.env-example" .env
sed -i -E 's/^DOMAIN=.*/DOMAIN=terrarun/g' .env
sed -i -E 's#^BASE_URL=.*#BASE_URL=https://terrarun#g' .env

# Just in case of leftovers from previous run.
if [ $RESET = true ]; then
    docker compose down
fi

# Build UI and api containers
if [ $BUILD = true ]; then
    docker compose build api ui
fi

# Startup base containers for setup
docker compose up -d traefik api db minio createbucket

# @TODO Replace with a proper wait.
# sleep 15

docker compose exec -ti api alembic upgrade head

TFE_TOKEN=$(docker compose exec -e PYTHONPATH=/app: -ti api python tests/e2e/scripts/bootstrap_admin.py)

# @TODO Replace with curl or something.
AGENT_TOKEN=$(docker compose exec -e PYTHONPATH=/app: -ti api python tests/e2e/scripts/bootstrap_agent_pool.py)

# Set token
sed -i -E "s#^TFC_AGENT_TOKEN=.*#TFC_AGENT_TOKEN=${AGENT_TOKEN}#g" .env

# Bring up remaining containers
docker compose up -d

# Run terraform executing test
timeout --signal=TERM --foreground 3m docker compose run --rm -i -w /tests/terraform/execution test-runner test

# Run tfe provider compatibility tests
timeout --signal=TERM --foreground 3m docker compose run --rm -i -w /tests/terraform/tfe_provider test-runner test

# Teardown stack
finish
