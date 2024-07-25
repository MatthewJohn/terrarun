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
    cp ./pki/issued/terrarun.crt $TERRARUN_DIR/ssl/public.pem
popd

# Get IP of docker host to setup hosts file
hex_ip=$(cat /proc/net/route | head -2 | tail -1 | awk '{print $3}')
ip=$(for i in $(echo "$hex_ip" | sed -E 's/(..)(..)(..)(..)/\4 \3 \2 \1/' ) ; do 
    printf "%d." $((16#$i));
done | sed 's/.$//')

echo "$ip terrarun" >> /etc/hosts

cp .env-example .env
sed -E 's/DOMAIN=.*/DOMAIN=terrarun/g' .env
sed -E 's#BASE_URL=.*#BASE_URL=https://terrarun#g' .env

# Run basic tests to check terrarun can come up
docker compose up --build -d

# Trap errors destroy stack
error() {
    cd $TERRARUN_DIR
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
export TFE_TOKEN=$(grep 'Created admin token' ./setup_output.log | sed 's/Created admin token: //g')
echo "Admin token: $TFE_TOKEN"
lifecycle_id=$(grep 'Created lifecycle' ./setup_output.log | sed 's/Created lifecycle: //g')
echo "Lifecycle ID: $lifecycle_id"
agent_token=$(grep 'Created agent token' ./setup_output.log | sed 's/Created agent token: //g')
echo "Agent Token: $agent_token"

# Run terraform to setup
pushd tests/smoke/terraform/setup
  terraform init
  terraform apply -auto-approve
popd

# Use the API endpoint to create a project
curl 'https://terrarun/api/v2/organizations/smoke-test-org/projects' \
    -X POST \
    -H 'Authorization: Bearer KCTfieKEQ9Ohvc.terrav1.04qP283DMVgAFL0iGPO4icpCofCfMt7yciTWkSzC33tDX9hhzcZgyv83fGr0gM8F8FN' \
    -H 'Content-Type: application/json' \
    --data-raw '{"data":{"type":"projects","attributes":{"name":"smoketest","description":"Smoke Test Project","lifecycle":"'$lifecycle_id'"}}}'

# Start agent
tfc-agent -address https://terrarun -token=$agent_token -log-level=TRACE  -auto-update=disabled &
tfc_agent_pid=$!
sleep 30


# Kill agent
kill -9 $tfc_agent_pid

# Teardown stack
cd $TERRARUN_DIR
docker compose down --volumes
