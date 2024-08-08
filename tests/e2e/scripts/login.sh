#!/bin/sh

set -eu

cat << EOF > /root/.terraform.d/credentials.tfrc.json
{
  "credentials": {
    "terrarun": {
      "token": "$1"
    }
}
EOF

echo Set token to $1
