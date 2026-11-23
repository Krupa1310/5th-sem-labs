# One-screen status of everything this project runs.
kubectl get pods -l "app in (health-demo,health-dashboard)" -o wide
kubectl get svc health-demo-svc health-dashboard
kubectl get pvc student-data
kubectl get endpoints health-demo-svc
Write-Host "`nRecent probe-related events:" -ForegroundColor Cyan
kubectl get events --sort-by=.lastTimestamp | Select-String -Pattern "Unhealthy|Killing|Started|Pulled|BackOff" | Select-Object -Last 12
