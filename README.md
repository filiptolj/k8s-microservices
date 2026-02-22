# k8s-microservices

A two-service Python microservices project with full CI/CD, Docker, and Kubernetes support.

**service1** generates the current UTC timestamp. **service2** accepts a format type (`iso` or `timestamp`), calls service1, and returns the formatted date. Traffic enters through an nginx ingress, hits service2, which calls service1 internally. Communication between services is restricted by a NetworkPolicy so service1 can only be reached by service2.

## Folder Structure

### `service1/`
UTC timestamp generator service. Reads a format type from stdin and prints either an ISO 8601 timestamp or a Unix timestamp. Built as a Docker image using the OpenFaaS classic watchdog.

### `service2/`
Timestamp formatter service. Accepts a format type from stdin, forwards it to service1, and returns the formatted date (`YYYY-MM-DD`). Built as a Docker image using the OpenFaaS classic watchdog.

### `k8s/`
Raw Kubernetes manifests for deploying both services to a local cluster (Minikube). Organised into subdirectories by resource scope:
- `base/` — namespace and ingress
- `service1/` — deployment, service, networkpolicy
- `service2/` — deployment, service, configmap

### `helm/`
Helm charts for deploying both services. Three separate charts:
- `service1/` — deploys the service1 workload
  ```bash
  helm upgrade --install service1 helm/service1/ --namespace demo-svcs --create-namespace
  ```
- `service2/` — deploys the service2 workload
  ```bash
  helm upgrade --install service2 helm/service2/ --namespace demo-svcs
  ```
- `ingress/` — deploys the nginx ingress and auto-generates a self-signed TLS certificate
  ```bash
  helm upgrade --install ingress helm/ingress/ --namespace demo-svcs
  ```

### `scripts/`
Deployment automation scripts:
- `bash/deploy.sh` — deploys the full cluster using raw kubectl manifests
  ```bash
  ./scripts/bash/deploy.sh
  ```
- `bash/helm-deploy.sh` — deploys the full cluster using Helm
  ```bash
  ./scripts/bash/helm-deploy.sh
  ```
- `bash/setup-ingress.sh` — standalone script for TLS cert generation and ingress setup
  ```bash
  ./scripts/bash/setup-ingress.sh
  ```
- `python/deploy.py` — Docker-based local deployment with configurable image versions and ports
  ```bash
  ./scripts/python/deploy.py --version_service1=1.0.0 --version_service2=1.0.1
  ./scripts/python/deploy.py --version_service1=1.0.0 --version_service2=1.0.1 --startup_timeout=30 --cleanup
  ```

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

### CI (`ci.yml`)
Triggered on pull requests and pushes to non-main branches. Only runs for services with detected file changes.
- `changes` — detects which services have changed using path filters
- `ci-service1` — runs if service1 files changed
  - Install test dependencies
  - Run unit tests
  - Build Docker image (no push)
- `ci-service2` — runs if service2 files changed
  - Install test dependencies
  - Run unit tests
  - Build Docker image (no push)

### CD (`cd.yml`)
Triggered on merge to `main`. Only runs for services with detected file changes.
- `changes` — detects which services have changed using path filters
- `publish-service1` — runs if service1 files changed
  - Read version from `service1/VERSION`
  - Run unit tests
  - Build and push Docker image to Docker Hub (`service1-<version>` and `service1-latest`)
  - Create git tag (`service1-v<version>`)
- `publish-service2` — runs if service2 files changed
  - Read version from `service2/VERSION`
  - Run unit tests
  - Build and push Docker image to Docker Hub (`service2-<version>` and `service2-latest`)
  - Create git tag (`service2-v<version>`)
