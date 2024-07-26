#!/bin/bash

set -e
set -x

# Setup CA certificates and server certs
mkdir easy-rsa
cp -r /usr/share/easy-rsa/* ./easy-rsa/

TERRARUN_DIR=`pwd`

pushd ./easy-rsa
    export EASYRSA_BATCH=1
    ./easyrsa init-pki

    cat > ./pki/vars <<'EOF'
set_var EASYRSA_REQ_COUNTRY    "GB"
set_var EASYRSA_REQ_PROVINCE   "Hampshire"
set_var EASYRSA_REQ_CITY       "Southampton"
set_var EASYRSA_REQ_ORG        "Terrarun"
set_var EASYRSA_REQ_EMAIL      "admin@example.com"
set_var EASYRSA_REQ_OU         "Community"
set_var EASYRSA_REQ_CN         "terrarun"
set_var EASYRSA_ALGO           "ec"
set_var EASYRSA_DIGEST         "sha512"
EOF

    ./easyrsa build-ca nopass
    cp ./pki/ca.crt /usr/local/share/ca-certificates/
    update-ca-certificates

    openssl genrsa -out $TERRARUN_DIR/ssl/private.pem
    openssl req -new -key $TERRARUN_DIR/ssl/private.pem -out server.req -subj \
        /C=GB/ST=Hampshire/L=Southampton/O=Terrarun/OU=Community/CN=terrarun

    ./easyrsa import-req ./server.req terrarun
    ./easyrsa sign-req server terrarun
    # Remove any lines before the cert that start with whitespace or 'Certificate'
    cat ./pki/issued/terrarun.crt | grep -Ev '^\s+' | grep -Ev '^Certificate' > $TERRARUN_DIR/ssl/public.pem
popd

# Get IP of docker host to setup hosts file
hex_ip=$(cat /proc/net/route | head -2 | tail -1 | awk '{print $3}')
ip=$(for i in $(echo "$hex_ip" | sed -E 's/(..)(..)(..)(..)/\4 \3 \2 \1/' ) ; do 
    printf "%d." $((16#$i));
done | sed 's/.$//')

echo "$ip terrarun" >> /etc/hosts

cp .env-example .env
sed -i -E 's/^DOMAIN=.*/DOMAIN=terrarun/g' .env
sed -i -E 's#^BASE_URL=.*#BASE_URL=https://terrarun#g' .env

# Startup base containers for setup
docker compose -f docker-compose.yml -f ./tests/e2e/docker-compose.yml up --build -d traefik api db minio createbucket

# Trap errors destroy stack
error() {
    cd $TERRARUN_DIR
    docker compose logs
    docker compose down --volumes
    exit 1
}
trap error ERR

sleep 30

docker compose exec -ti api \
    python ./bin/initial_setup.py \
        --migrate-database \
        --organisation-email=test@localhost.com \
        --admin-username=admin \
        --admin-email=admin@localhost \
        --admin-password=password \
        --create-admin-token \
        --global-agent-pool=default-pool | tee ./setup_output.log

# Obtain token from output
export TFE_TOKEN=$(grep 'Created admin token:' ./setup_output.log | sed 's/Created admin token: //g')
echo "Admin token: $TFE_TOKEN"
lifecycle_id=$(grep 'Created lifecycle:' ./setup_output.log | sed 's/Created lifecycle: default //g')
echo "Lifecycle ID: $lifecycle_id"
agent_token=$(grep 'Created agent token:' ./setup_output.log | sed 's/Created agent token: //g')
echo "Agent Token: $agent_token"

# Bring up remaining containers
docker compose -f docker-compose.yml -f ./tests/e2e/docker-compose.yml up -d

# Run terraform to setup
pushd tests/e2e/terraform/setup
    timeout --signal=TERM 1m \
        terraform init
    timeout --signal=TERM 1m \
        terraform apply -auto-approve
popd

# Use the API endpoint to create a project
curl 'https://terrarun/api/v2/organizations/smoke-test-org/projects' \
    -X POST \
    -H "Authorization: Bearer $TFE_TOKEN" \
    -H 'Content-Type: application/json' \
    --fail \
    --output ./project.json \
    --data-raw '{"data":{"type":"projects","attributes":{"name":"smoketest","description":"Smoke Test Project","lifecycle":"'$lifecycle_id'"}}}'

project_id=$(cat project.json | jq -r '.data.id')

# Create Terraform tool
curl 'https://terrarun/api/v2/admin/terraform-versions' \
    -X POST \
    -H "Authorization: Bearer $TFE_TOKEN" \
    -H 'Content-Type: application/json' \
    --fail \
    --data-raw '{"type":"terraform-versions","attributes":{"version":"1.4.5","url":"","checksum-url":"","sha":"","deprecated":false,"enabled":true}}'

# Assign Terraform tool to project
curl "https://terrarun/api/v2/projects/$project_id" \
    -X PATCH \
    -H "Authorization: Bearer $TFE_TOKEN" \
    -H 'Content-Type: application/json' \
    --fail \
    --data-raw '{"data":{"type":"projects","attributes":{"terraform-version":"1.4.5"}}}'

# Start agent
tfc-agent -address https://terrarun -token=$agent_token -log-level=TRACE  -auto-update=disabled &
tfc_agent_pid=$!
sleep 10

# Create Terraform credential file
cat > ~/.terraformrc <<EOF
credentials "terrarun" {
  token = "$TFE_TOKEN"
}
EOF

# Run test Terraform
pushd tests/e2e/terraform/execution
    timeout --signal=TERM 1m \
        terraform init
    timeout --signal=TERM 3m \
        terraform plan
    timeout --signal=TERM 3m \
        terraform apply -auto-approve
popd

# Kill agent
kill -9 $tfc_agent_pid

# Teardown stack
cd $TERRARUN_DIR
docker compose down --volumes
