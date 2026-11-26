#!/usr/bin/env bash
# Build both Docker images, make them available to your cluster, and deploy everything.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v docker  >/dev/null || { echo "ERROR: docker not found";  exit 1; }
command -v kubectl >/dev/null || { echo "ERROR: kubectl not found"; exit 1; }
kubectl cluster-info >/dev/null 2>&1 || { echo "ERROR: no Kubernetes cluster reachable (see README > Troubleshooting)"; exit 1; }

CTX="$(kubectl config current-context)"
echo "==> Kubernetes context: $CTX"

echo "==> 1/4 Building Docker images"
docker build -t health-demo:2.0      app
docker build -t health-dashboard:2.0 dashboard

echo "==> 2/4 Making the images available to the cluster"
case "$CTX" in
  docker-desktop|docker-for-desktop) echo "   Docker Desktop shares its image store with Kubernetes - nothing to do." ;;
  minikube*) minikube image load health-demo:2.0 && minikube image load health-dashboard:2.0 ;;
  kind-*)    kind load docker-image health-demo:2.0 health-dashboard:2.0 --name "${CTX#kind-}" ;;
  k3d-*)     k3d image import health-demo:2.0 health-dashboard:2.0 -c "${CTX#k3d-}" ;;
  *) echo "   WARNING: unknown cluster type '$CTX'. If pods show ErrImagePull, load the images into your cluster (README > Troubleshooting)." ;;
esac

echo "==> 3/4 Applying Kubernetes manifests"
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl apply -f k8s/dashboard-rbac.yaml -f k8s/dashboard.yaml

echo "==> 4/4 Waiting for pods to become Ready"
kubectl rollout status deployment/health-demo --timeout=180s
kubectl rollout status deployment/health-dashboard --timeout=180s

echo
kubectl get pods -o wide
kubectl get pvc student-data
kubectl get endpoints health-demo-svc
echo
echo "Student app: http://localhost:30080   Dashboard: http://localhost:30090"
echo "(not reachable? ./scripts/open-dashboard.sh forwards the dashboard to http://localhost:8080)"
