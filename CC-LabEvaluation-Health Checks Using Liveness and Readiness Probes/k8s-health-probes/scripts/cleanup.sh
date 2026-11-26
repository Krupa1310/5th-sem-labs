#!/usr/bin/env bash
# Remove the app + dashboard from the cluster. The student database volume (PVC) is KEPT unless --purge.
cd "$(dirname "$0")/.."
kubectl delete -f k8s/dashboard.yaml -f k8s/dashboard-rbac.yaml -f k8s/service.yaml -f k8s/deployment.yaml --ignore-not-found
if [ "${1:-}" = "--purge" ]; then kubectl delete -f k8s/pvc.yaml --ignore-not-found; echo "PVC deleted - student data is gone."
else echo "Student data volume 'student-data' kept (use --purge to delete it too)."; fi
echo "(Docker images remain; delete with: docker rmi health-demo:2.0 health-dashboard:2.0)"
