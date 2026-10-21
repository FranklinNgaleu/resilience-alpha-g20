#!/bin/bash
set -e
cd "$(dirname "$0")/.."
docker run --rm \
  --network none \
  -v "$PWD":"$PWD" -w "$PWD" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  resilience-ansible:local \
  ansible-playbook -i infra/ansible/inventory.ini "$@"
