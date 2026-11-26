<#
 Remove the application and dashboard from the cluster. The student database volume is KEPT
 (so your records survive) unless you pass -Purge.
   .\scripts\cleanup.ps1            # keep the data
   .\scripts\cleanup.ps1 -Purge     # also delete the PVC (all student records are lost)
#>
param([switch]$Purge)
Set-Location (Split-Path -Parent $PSScriptRoot)
kubectl delete -f k8s/dashboard.yaml -f k8s/dashboard-rbac.yaml -f k8s/service.yaml -f k8s/deployment.yaml --ignore-not-found
if ($Purge) { kubectl delete -f k8s/pvc.yaml --ignore-not-found; Write-Host "PVC deleted - student data is gone." -ForegroundColor Yellow }
else        { Write-Host "Student data volume 'student-data' kept. Use -Purge to delete it too." }
