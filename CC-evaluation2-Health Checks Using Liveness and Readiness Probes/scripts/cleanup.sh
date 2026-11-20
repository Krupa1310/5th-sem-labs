#!/usr/bin/env bash
# Remove everything this project created in the cluster.
cd "$(dirname "$0")/.."
kubectl delete -f k8s/dashboard.yaml -f k8s/dashboard-rbac.yaml -f k8s/service.yaml -f k8s/deployment.yaml --ignore-not-found
echo "Removed. (Docker images remain; delete with: docker rmi health-demo:1.0 health-dashboard:1.0)"
