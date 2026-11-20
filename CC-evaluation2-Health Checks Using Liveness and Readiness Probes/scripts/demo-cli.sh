#!/usr/bin/env bash
# Terminal-only demo using plain kubectl (handy for showing the evaluator the raw commands).
#   ./scripts/demo-cli.sh status      show pods, restarts and Service endpoints
#   ./scripts/demo-cli.sh liveness    break /healthz on the first pod
#   ./scripts/demo-cli.sh readiness   break /ready on the first pod
#   ./scripts/demo-cli.sh slowstart   30 s start-up delay (rolling update)
#   ./scripts/demo-cli.sh restore     undo everything
#   ./scripts/demo-cli.sh watch       live view (kubectl get pods -w)
set -euo pipefail
LABEL="app=health-demo"
run() { echo; echo "\$ $*"; "$@"; }
first_pod() { kubectl get pods -l "$LABEL" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}'; }
# The app image has Python but no curl, so we call the pod's control endpoint with Python.
poke() {  # poke <pod> <path>
  kubectl exec "$1" -- python -c "import urllib.request as u;print(u.urlopen(u.Request('http://localhost:5000$2',data=b'{}',method='POST',headers={'Content-Type':'application/json'})).read().decode())"
}
status() { run kubectl get pods -l "$LABEL" -o wide; run kubectl get endpoints health-demo-svc; }

case "${1:-}" in
  status)    status ;;
  liveness)
    POD=$(first_pod); echo "Target pod: $POD"
    run poke "$POD" /control/liveness
    echo; echo "Kubelet needs 3 failed probes (3 x 5 s = ~15 s). Watching (Ctrl+C when RESTARTS becomes 1)..."
    kubectl get pods -l "$LABEL" -w
    echo; echo "Afterwards run:"; echo "  kubectl describe pod $POD | tail -15"; echo "  kubectl logs $POD --previous | tail" ;;
  readiness)
    POD=$(first_pod); echo "Target pod: $POD"
    run poke "$POD" /control/readiness
    echo; echo "After ~15 s the pod shows 0/1 and its IP leaves the endpoints (Ctrl+C to stop watching)."
    kubectl get pods -l "$LABEL" -w ;;
  slowstart)
    run kubectl set env deployment/health-demo STARTUP_DELAY_SECONDS=30
    echo; echo "New pods will be Running but 0/1 for ~30 s (Ctrl+C to stop watching)."
    kubectl get pods -l "$LABEL" -w ;;
  restore)
    run kubectl set env deployment/health-demo STARTUP_DELAY_SECONDS=0
    kubectl rollout status deployment/health-demo --timeout=120s
    for p in $(kubectl get pods -l "$LABEL" -o name); do run poke "${p#pod/}" /control/reset; done
    status ;;
  watch)     kubectl get pods -l "$LABEL" -w ;;
  *) sed -n '2,9p' "$0"; exit 1 ;;
esac
