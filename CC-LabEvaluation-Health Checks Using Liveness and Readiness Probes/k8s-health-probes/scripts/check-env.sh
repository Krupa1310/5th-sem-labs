#!/usr/bin/env bash
# Step 0: is my laptop ready? Checks Docker, kubectl and that a Kubernetes cluster answers.
ok=1
check() { if command -v "$1" >/dev/null 2>&1; then echo "  [ok]   $1 found: $($2 2>&1 | head -1)"; else echo "  [MISS] $1 not found - $3"; ok=0; fi; }
echo "Checking tools..."
check docker  "docker --version"            "install Docker Desktop (https://www.docker.com/products/docker-desktop)"
check kubectl "kubectl version --client"    "comes with Docker Desktop / install from https://kubernetes.io/docs/tasks/tools/"
if docker info >/dev/null 2>&1; then echo "  [ok]   Docker daemon is running"; else echo "  [FAIL] Docker daemon not reachable - start Docker Desktop"; ok=0; fi
echo "Checking Kubernetes cluster..."
if kubectl cluster-info >/dev/null 2>&1; then
  echo "  [ok]   cluster reachable, context = $(kubectl config current-context)"
  kubectl get nodes
else
  echo "  [FAIL] no cluster reachable. Enable Kubernetes in Docker Desktop, or run: minikube start  /  kind create cluster"; ok=0
fi
[ $ok = 1 ] && echo "All good - run ./scripts/deploy.sh" || { echo "Fix the items above, then re-run."; exit 1; }
