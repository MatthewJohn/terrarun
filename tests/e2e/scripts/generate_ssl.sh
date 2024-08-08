#!/bin/bash

set -ex

if [ -f /certs/public.pem ]; then
  echo "Certs already available." >&2
  exit 0
fi


# Setup CA certificates and server certs
mkdir easy-rsa
cp -r /usr/share/easy-rsa/* ./easy-rsa/

cd ./easy-rsa
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

mkdir -p /usr/local/share/ca-certificates/
cp ./pki/ca.crt /usr/local/share/ca-certificates/terrarunCA.crt
update-ca-certificates

cp /etc/ssl/certs/ca-certificates.crt /certs/ca-certificates.crt

openssl genrsa -out /certs/private.pem
openssl req -new -key /certs/private.pem -out server.req -subj \
    /C=GB/ST=Hampshire/L=Southampton/O=Terrarun/OU=Community/CN=terrarun

./easyrsa import-req ./server.req terrarun
./easyrsa sign-req server terrarun

# Remove any lines before the cert that start with whitespace or 'Certificate'
grep -Ev '^(\s|Certificate)' ./pki/issued/terrarun.crt > /certs/public.pem