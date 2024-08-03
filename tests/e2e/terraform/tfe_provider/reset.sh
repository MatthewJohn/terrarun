#!/bin/bash

set -euo pipefail

LIST=$(curl \
    --fail -s --show-error \
    --request GET \
    -H 'Host: terrarun' \
    -H 'Authorization: Bearer 5Zj5bpBpnP544K.terrav1.2NI3lGIXTzZetUEVml9xQbc2Tth0WWCaxuP6XwNt1SiHLbYGUOjkBKcf39tHgSWNirA' \
    --url 'https://localhost/api/v2/admin/terraform-versions?search%5Bversion%5D=1.6.'
)

VERSIONS=$(echo $LIST | jq -r '.data[].id')

for version in $VERSIONS; do
  curl \
    --fail -s --show-error \
    --request DELETE \
    -H 'Host: terrarun' \
    -H 'Authorization: Bearer 5Zj5bpBpnP544K.terrav1.2NI3lGIXTzZetUEVml9xQbc2Tth0WWCaxuP6XwNt1SiHLbYGUOjkBKcf39tHgSWNirA' \
    --url "https://localhost/api/v2/admin/terraform-versions/${version}"
done



LIST=$(curl \
    --fail -s --show-error \
    --request GET \
    -H 'Host: terrarun' \
    -H 'Authorization: Bearer 5Zj5bpBpnP544K.terrav1.2NI3lGIXTzZetUEVml9xQbc2Tth0WWCaxuP6XwNt1SiHLbYGUOjkBKcf39tHgSWNirA' \
    --url 'https://localhost/api/v2/admin/terraform-versions?search%5Bversion%5D=1.5.'
)

VERSIONS=$(echo $LIST | jq -r '.data[].id')

for version in $VERSIONS; do
  curl \
    --fail -s --show-error \
    --request DELETE \
    -H 'Host: terrarun' \
    -H 'Authorization: Bearer 5Zj5bpBpnP544K.terrav1.2NI3lGIXTzZetUEVml9xQbc2Tth0WWCaxuP6XwNt1SiHLbYGUOjkBKcf39tHgSWNirA' \
    --url "https://localhost/api/v2/admin/terraform-versions/${version}"
done