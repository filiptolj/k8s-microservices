#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/../.."
NAMESPACE="demo-svcs"
HOST="demo-svcs.local"

echo "==> Checking prerequisites..."
for cmd in helm kubectl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '${cmd}' is not installed"
        exit 1
    fi
done

echo ""
echo "=== Deploying to Kubernetes via Helm ==="
echo ""

echo "==> [1/3] Installing service1..."
helm upgrade --install service1 "${ROOT_DIR}/helm/service1/" \
    --namespace "${NAMESPACE}" \
    --create-namespace

echo "==> [2/3] Installing service2..."
helm upgrade --install service2 "${ROOT_DIR}/helm/service2/" \
    --namespace "${NAMESPACE}"

echo "==> [3/3] Installing ingress and TLS..."
helm upgrade --install ingress "${ROOT_DIR}/helm/ingress/" \
    --namespace "${NAMESPACE}"

echo "==> Checking /etc/hosts for ${HOST}..."
if grep -q "${HOST}" /etc/hosts; then
    echo "    Entry already exists, skipping."
else
    echo "    Adding '127.0.0.1 ${HOST}' to /etc/hosts (requires sudo)..."
    echo "127.0.0.1 ${HOST}" | sudo tee -a /etc/hosts > /dev/null
fi

echo ""
echo "==> Waiting for deployments to be ready..."
kubectl rollout status deployment/service1 -n "${NAMESPACE}" --timeout=120s
kubectl rollout status deployment/service2 -n "${NAMESPACE}" --timeout=120s

echo ""
echo "=== Deployment successful! ==="
echo ""
echo "Make sure 'sudo -E minikube tunnel' is running, then test with:"
echo "  echo 'iso' | curl -sk -X POST https://${HOST} --data-binary @-"
