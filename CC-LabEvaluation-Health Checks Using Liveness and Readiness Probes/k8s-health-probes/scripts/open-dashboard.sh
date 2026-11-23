#!/usr/bin/env bash
# Forward the dashboard to http://localhost:8080 (works on every kind of local cluster).
# Leave this terminal open while you demo. Press Ctrl+C to stop.
echo "Dashboard -> http://localhost:8080"
exec kubectl port-forward svc/health-dashboard 8080:80
