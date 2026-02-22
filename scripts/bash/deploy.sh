#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="demo-svcs"

echo "==> Checking prerequisites..."
for cmd in kubectl openssl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '${cmd}' is not installed"
        exit 1
    fi
done

echo ""
echo "=== Deploying to Kubernetes ==="
echo ""

ROOT_DIR="${SCRIPT_DIR}/../.."

echo "==> [1/4] Applying namespace..."
kubectl apply -f "${ROOT_DIR}/k8s/base/namespace.yaml"

echo "==> [2/4] Deploying service1..."
kubectl apply -f "${ROOT_DIR}/k8s/service1/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/service1/service.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/service1/networkpolicy.yaml"

echo "==> [3/4] Deploying service2..."
kubectl apply -f "${ROOT_DIR}/k8s/service2/configmap.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/service2/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/service2/service.yaml"

echo "==> [4/4] Setting up ingress and tls..."
bash "${SCRIPT_DIR}/setup-ingress.sh"

echo ""
echo "==> Waiting for deployments to be ready..."
kubectl rollout status deployment/service1 -n "${NAMESPACE}" --timeout=120s
kubectl rollout status deployment/service2 -n "${NAMESPACE}" --timeout=120s

echo ""
echo "=== Deployment successful! ==="
echo ""
echo "Make sure 'sudo -E minikube tunnel' is running, then test with:"
echo "  echo 'iso' | curl -sk -X POST https://demo-svcs.local --data-binary @-"
