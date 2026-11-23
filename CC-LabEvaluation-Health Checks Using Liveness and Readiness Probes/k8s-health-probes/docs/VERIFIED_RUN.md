# Verified run (real output)

> **Scope note (added with the Student Management upgrade):** this captured run is from the *original* project
> (images `:1.0`, no database, no startup probe). It is kept as evidence that the three probe scenarios and the dashboard
> worked on a real cluster. The student application, PVC, startup probe, DB-aware readiness and automatic demo mode were
> added afterwards and are covered by the offline tests described in the README (§0), not by this run.


This is the **actual, unedited output** from running this project on a real Kubernetes cluster
(k3s v1.30.5, single node) during development. Nothing here is mocked.

> **Note on the test environment.** The development sandbox had no Docker, so the two images were
> assembled from the same source files and imported straight into the cluster's container runtime
> instead of using `docker build`. On your laptop you will use `docker build` (done for you by
> `scripts/deploy.sh`). Everything *above* the image layer - the Flask code, the manifests, the probes,
> the dashboard and the Kubernetes behaviour - is exactly what you are shipping.
> The `docker build`, `minikube image load` / `kind load` paths in `scripts/deploy.sh` could **not** be
> tested in that sandbox (see README > Troubleshooting if they misbehave).

## 1. Automated check: `python tests/verify_scenarios.py`  (23 / 23 checks passed)

```text
== Pre-flight: all pods Running, 1/1 Ready, all IPs in Service endpoints
  [PASS] 3 pods are Running and 1/1 Ready
  [PASS] Service endpoints list every pod IP   <- 10.42.0.35, 10.42.0.36, 10.42.0.37
NAME                          READY   STATUS    RESTARTS   AGE
      health-demo-5d9455b97-qbjv9   1/1     Running   0          2m5s
      health-demo-5d9455b97-rvlkz   1/1     Running   0          2m5s
      health-demo-5d9455b97-vxjnc   1/1     Running   0          2m5s

== Scenario A: LIVENESS failure
  target pod: health-demo-5d9455b97-qbjv9   restarts before: 0
  injected: /healthz now returns 500 (kubelet needs 3 failures x 5 s = ~15 s)
  [PASS] kubelet restarted the container automatically
  [PASS] describe/events show 'Liveness probe failed'   <- Unhealthy   Liveness probe failed: HTTP probe failed with statuscode: 500
  [PASS] events show the container being killed for restart
  [PASS] pod recovered: Running and 1/1 Ready again
  [PASS] restart count increased by exactly 1   <- 0 -> 1
  [PASS] pod IP is back in the Service endpoints
NAME                          READY   STATUS    RESTARTS   AGE
      health-demo-5d9455b97-qbjv9   1/1     Running   1          2m22s
      health-demo-5d9455b97-rvlkz   1/1     Running   0          2m22s
      health-demo-5d9455b97-vxjnc   1/1     Running   0          2m22s

== Scenario B: READINESS failure
  target pod: health-demo-5d9455b97-qbjv9 (10.42.0.36)   restarts before: 1
  injected: /ready now returns 503
  [PASS] READY changed 1/1 -> 0/1
  [PASS] pod is still Running   <- Running
  [PASS] restart count did NOT increase   <- 1 -> 1
  [PASS] pod IP removed from Service endpoints (ready list)   <- ready=['10.42.0.35', '10.42.0.37']
  [PASS] 30 requests via the Service: none reached the NotReady pod   <- {'health-demo-5d9455b97-vxjnc': 12, 'health-demo-5d9455b97-rvlkz': 18}
NAME                          READY   STATUS    RESTARTS   AGE
      health-demo-5d9455b97-qbjv9   0/1     Running   1          2m39s
      health-demo-5d9455b97-rvlkz   1/1     Running   0          2m39s
      health-demo-5d9455b97-vxjnc   1/1     Running   0          2m39s
  restoring readiness ...
  [PASS] READY returned to 1/1
  [PASS] pod IP added back to Service endpoints
  [PASS] restart count still unchanged   <- 1
NAME                          READY   STATUS    RESTARTS   AGE
      health-demo-5d9455b97-qbjv9   1/1     Running   1          2m41s
      health-demo-5d9455b97-rvlkz   1/1     Running   0          2m41s
      health-demo-5d9455b97-vxjnc   1/1     Running   0          2m41s

== Scenario C: SLOW START-UP (30 s)
  patched Deployment: STARTUP_DELAY_SECONDS=30  -> rolling update begins
  [PASS] a NEW pod is Running but NotReady (0/1) while initialising
  [PASS] NotReady pod is not in the Service's ready endpoints   <- ip=10.42.0.39
  [PASS] no restarts while starting slowly (liveness stays happy)
NAME                           READY   STATUS    RESTARTS   AGE
      health-demo-5d9455b97-qbjv9    1/1     Running   1          2m45s
      health-demo-5d9455b97-rvlkz    1/1     Running   0          2m45s
      health-demo-5d9455b97-vxjnc    1/1     Running   0          2m45s
      health-demo-776678d7db-bqmfj   0/1     Running   0          3s
      health-demo-776678d7db-grr89   0/1     Running   0          3s
      health-demo-776678d7db-pfgj9   0/1     Running   0          3s
  [PASS] 30 requests via the Service: none sent to the initialising pods   <- {'health-demo-5d9455b97-vxjnc': 10, 'health-demo-5d9455b97-rvlkz': 9, 'health-demo-5d9455b97-qbjv9': 11}
  [PASS] no failed requests during the rollout (old pods keep serving)
  [PASS] after ~30 s all new pods became 1/1 Ready
  [PASS] all new pod IPs are now in the Service endpoints
NAME                           READY   STATUS        RESTARTS   AGE
      health-demo-5d9455b97-qbjv9    1/1     Terminating   1          3m18s
      health-demo-5d9455b97-rvlkz    1/1     Terminating   0          3m18s
      health-demo-5d9455b97-vxjnc    1/1     Terminating   0          3m18s
      health-demo-776678d7db-bqmfj   1/1     Running       0          36s
      health-demo-776678d7db-grr89   1/1     Running       0          36s
      health-demo-776678d7db-pfgj9   1/1     Running       0          36s
  restoring: STARTUP_DELAY_SECONDS=0 ...

==== 23/23 checks passed ====
```

## 2. What `kubectl describe` / `kubectl logs --previous` showed after a liveness failure

```text
$ kubectl get pods
NAME                          READY   STATUS    RESTARTS      AGE
health-demo-5d9455b97-9mmxp   1/1     Running   1 (24s ago)   2m50s
health-demo-5d9455b97-jr2lb   1/1     Running   0             2m50s
health-demo-5d9455b97-zhwqk   1/1     Running   0             2m50s

$ kubectl describe pod health-demo-5d9455b97-9mmxp   (last lines)
Events:
  Type     Reason     Age                  From               Message
  ----     ------     ----                 ----               -------
  Normal   Scheduled  2m50s                default-scheduler  Successfully assigned default/health-demo-5d9455b97-9mmxp to vm
  Normal   Pulled     25s (x2 over 2m50s)  kubelet            Container image "health-demo:1.0" already present on machine
  Normal   Created    25s (x2 over 2m50s)  kubelet            Created container health-demo
  Normal   Started    25s (x2 over 2m50s)  kubelet            Started container health-demo
  Warning  Unhealthy  25s (x3 over 35s)    kubelet            Liveness probe failed: HTTP probe failed with statuscode: 500
  Normal   Killing    25s                  kubelet            Container health-demo failed liveness probe, will be restarted
    Last State:     Terminated
      Reason:       Completed
      Exit Code:    0
    Restart Count:  1
    Liveness:   http-get http://:5000/healthz delay=5s timeout=1s period=5s #success=1 #failure=3
    Readiness:  http-get http://:5000/ready delay=3s timeout=1s period=5s #success=1 #failure=3
  Type     Reason     Age                  From               Message

$ kubectl logs health-demo-5d9455b97-9mmxp --previous | tail -6
10.42.0.1 - - [16/Nov/2026 04:33:27] "GET /healthz HTTP/1.1" 500 -
10.42.0.1 - - [16/Nov/2026 04:33:32] "GET /healthz HTTP/1.1" 500 -
10.42.0.1 - - [16/Nov/2026 04:33:32] "GET /ready HTTP/1.1" 200 -
10.42.0.1 - - [16/Nov/2026 04:33:37] "GET /ready HTTP/1.1" 200 -
10.42.0.1 - - [16/Nov/2026 04:33:37] "GET /healthz HTTP/1.1" 500 -
[health-demo-5d9455b97-9mmxp] SIGTERM received, shutting down
```

Things to point out to your evaluator in the output above:

* `Liveness: http-get http://:5000/healthz delay=5s timeout=1s period=5s #success=1 #failure=3` and
  `Readiness: ... delay=3s ... period=5s` - the probe settings from the brief, as Kubernetes stored them.
* `Warning Unhealthy ... Liveness probe failed: HTTP probe failed with statuscode: 500` - the failed health check.
* `Normal Killing ... failed liveness probe, will be restarted` - Kubernetes' automatic reaction.
* `Restart Count: 1` / `RESTARTS 1 (24s ago)` - the updated restart count.
* `--previous` logs show the old container answering `GET /healthz ... 500` until it was stopped.
* "Last State: Terminated, Reason: Completed, Exit Code: 0" is because the app handles SIGTERM and exits
  cleanly when the kubelet stops it (this is deliberate - see `_graceful_exit` in `app/app.py`).

## 3. Dashboard API test (every button, against the live cluster)

Summary of what the dashboard reported (all values came from the Kubernetes API / the pods):

| Step | Dashboard showed |
|------|------------------|
| Baseline | 3 pods, 3 healthy, 3/3 ready, restarts 0, endpoints = 3 IPs, scenario "None" |
| Liveness button | scenario "Liveness failure"; target pod liveness probe **Failing**; later restarts **0 -> 1**; events `Unhealthy` + `Killing`; back to HEALTHY |
| Readiness button | target pod **0/1**, readiness **Failing**, restarts unchanged; its IP moved to *NotReady* endpoints; 30 requests via Service reached only the other two pods |
| Restore (selected pod) | pod back to 1/1, IP back in ready endpoints |
| Slow Startup button | scenario "Slow startup"; 3 new pods Running **0/1** while 3 old pods kept serving; 30/30 requests succeeded; after ~30 s all new pods 1/1 |
| Restore Application Health | delay set back to 0 (rolling update), all failures cleared, HEALTHY |
| Bad requests | no pod selected -> HTTP 400 with message; unknown pod -> clear error; unknown action -> 404 |
