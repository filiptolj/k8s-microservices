#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/../.."
NAMESPACE="demo-svcs"
SECRET_NAME="demo-svcs-tls"
HOST="demo-svcs.local"
CERT_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "${CERT_DIR}"
}
trap cleanup EXIT

echo "==> Generating self-signed TLS certificate for ${HOST}..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${CERT_DIR}/tls.key" \
    -out "${CERT_DIR}/tls.crt" \
    -subj "/CN=${HOST}" \
    -addext "subjectAltName=DNS:${HOST}" \
    2>/dev/null

echo "==> Creating TLS secret '${SECRET_NAME}' in namespace '${NAMESPACE}'..."
if kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" &>/dev/null; then
    echo "    Secret already exists, replacing..."
    kubectl delete secret "${SECRET_NAME}" -n "${NAMESPACE}"
fi
kubectl create secret tls "${SECRET_NAME}" \
    --cert="${CERT_DIR}/tls.crt" \
    --key="${CERT_DIR}/tls.key" \
    -n "${NAMESPACE}"

echo "==> Applying ingress..."
kubectl apply -f "${ROOT_DIR}/k8s/base/ingress.yaml"

echo "==> Checking /etc/hosts for ${HOST}..."
if grep -q "${HOST}" /etc/hosts; then
    echo "    Entry already exists, skipping."
else
    echo "    Adding '127.0.0.1 ${HOST}' to /etc/hosts (requires sudo)..."
    echo "127.0.0.1 ${HOST}" | sudo tee -a /etc/hosts > /dev/null
fi