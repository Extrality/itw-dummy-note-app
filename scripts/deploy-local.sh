#!/usr/bin/env bash
# Reproduce the "Deploy preview" workflow from a laptop.
# CI uses the same kubeconfig: gh secret set KUBECONFIG_DATA < scripts/kubeconfig-ci.yaml
set -euo pipefail

cd "$(dirname "$0")/.."
export KUBECONFIG="$PWD/scripts/kubeconfig-ci.yaml"

docker build -t notes-app-api:latest ./note-app
docker build -t notes-app-web:latest ./note-web

kubectl apply -f k8s/
kubectl --namespace notes-app rollout status deploy/api --timeout=120s
