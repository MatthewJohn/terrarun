#!/bin/bash

DOMAIN=$1
if [ "$DOMAIN" == "" ]
then
  echo "Usage: thisscript.sh <domain>"
  exit 1
fi

mkdir -p example/ssl
pushd example/ssl

openssl genrsa -des3 -out myCA.key 2048
openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem
cp ./myCA.pem /usr/local/share/ca-certificates/
sudo cp ./myCA.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
openssl genrsa -out dev.key 2048
openssl req -new -key dev.key -out dev.csr

cat > dev.ext <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
EOF
openssl x509 -req -in dev.csr -CA myCA.pem -CAkey myCA.key \
  -CAcreateserial -out dev.crt -days 825 -sha256 -extfile dev.ext

popd
