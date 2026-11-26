<#
 Build both Docker images and deploy / upgrade everything on Docker Desktop Kubernetes.
 Safe to re-run. Nothing is deleted: the student database volume (PVC) is only ever created, never removed.

   cd k8s-health-probes
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1
#>
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$AppImage       = "health-demo:2.0"        # must match k8s/deployment.yaml
$DashboardImage = "health-dashboard:2.0"   # must match k8s/dashboard.yaml

function Step([string]$title, [scriptblock]$cmd) {
    Write-Host "==> $title" -ForegroundColor Cyan
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "Step failed: $title (exit code $LASTEXITCODE)" }
}

foreach ($tool in "docker", "kubectl") {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool not found. Install Docker Desktop and enable Kubernetes." }
}
$ctx = (kubectl config current-context).Trim()
Write-Host "Kubernetes context: $ctx"
if ($ctx -ne "docker-desktop") {
    Write-Warning "Expected context 'docker-desktop'. Switch with:  kubectl config use-context docker-desktop"
    throw "Wrong Kubernetes context: $ctx"
}

Step "1/6 Building the student application image ($AppImage)"  { docker build -t $AppImage app }
Step "2/6 Building the dashboard image ($DashboardImage)"      { docker build -t $DashboardImage dashboard }
Step "3/6 Creating the persistent volume claim (kept if it already exists)" { kubectl apply -f k8s/pvc.yaml }
Step "4/6 Deploying the student application (rolling update, 3 replicas)"   { kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml }
Step "5/6 Waiting for the student application"                 { kubectl rollout status deployment/health-demo --timeout=240s }
Step "6/6 Upgrading the monitoring dashboard in place"         { kubectl apply -f k8s/dashboard-rbac.yaml -f k8s/dashboard.yaml; kubectl rollout status deployment/health-dashboard --timeout=180s }

Write-Host ""
kubectl get pods -o wide
kubectl get pvc student-data
kubectl get endpoints health-demo-svc
Write-Host ""
Write-Host "Student application : http://localhost:30080" -ForegroundColor Green
Write-Host "Monitoring dashboard: http://localhost:30090" -ForegroundColor Green
Write-Host "(if a NodePort is not reachable:  kubectl port-forward svc/health-demo-svc 30080:80   and   kubectl port-forward svc/health-dashboard 30090:80)"
