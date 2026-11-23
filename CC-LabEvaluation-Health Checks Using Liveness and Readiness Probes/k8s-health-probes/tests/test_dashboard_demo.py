"""Dashboard tests against a FAKE Kubernetes API + fake pods (no cluster needed).
They check the dashboard's own logic: status aggregation, student-app info and the automatic demo mode
(safety rules, failure injection, detection and recovery tracking)."""
import unittest
from unittest import mock

import _helpers  # noqa: F401
import server


def info(**over):
    d = {"pod": "x", "liveness_failure_injected": False, "readiness_failure_injected": False,
         "startup_remaining_seconds": 0, "healthz_status": 200, "ready_status": 200,
         "last_kubelet_probe": {"liveness": {"status": 200, "age_seconds": 1}, "readiness": {"status": 200, "age_seconds": 1},
                                "startup": {"status": 200, "age_seconds": 60}},
         "kubelet_probe_counts": {"liveness": {"ok": 5, "fail": 0}, "readiness": {"ok": 5, "fail": 0}, "startup": {"ok": 2, "fail": 0}},
         "database": {"ok": True, "error": None, "initialised": True, "path": "/data/students.db", "students": 42}}
    d.update(over)
    return d


class FakeCluster:
    """Tiny in-memory stand-in for 3 pods; patches server.k8s / server.pod_call."""
    def __init__(self):
        self.pods = {f"health-demo-abc-{i}": {"ip": f"10.0.0.{i}", "ready": True, "restarts": 0, "info": info()} for i in range(3)}
        self.startup_delay, self.calls = 0, []

    def k8s(self, method, path, body=None, content_type=None):
        if "/pods" in path:
            return {"items": [{
                "metadata": {"name": n, "creationTimestamp": "2026-11-22T10:00:00Z"},
                "spec": {"nodeName": "docker-desktop", "containers": [{"name": "health-demo"}]},
                "status": {"podIP": p["ip"], "phase": "Running",
                           "conditions": [{"type": "Ready", "status": "True" if p["ready"] else "False"}],
                           "containerStatuses": [{"ready": p["ready"], "restartCount": p["restarts"], "state": {"running": {}}}]}}
                for n, p in self.pods.items()]}
        if "/deployments/" in path:
            return {"spec": {"replicas": 3, "template": {"spec": {"containers": [{
                        "name": "health-demo", "image": "health-demo:2.0",
                        "env": [{"name": "STARTUP_DELAY_SECONDS", "value": str(self.startup_delay)}],
                        "startupProbe": {"httpGet": {"path": "/startupz"}}, "livenessProbe": {}, "readinessProbe": {}}]}}},
                    "status": {"replicas": 3, "readyReplicas": 3, "updatedReplicas": 3, "availableReplicas": 3}}
        if "/endpoints/" in path:
            return {"subsets": [{"addresses": [{"ip": p["ip"], "targetRef": {"name": n}} for n, p in self.pods.items() if p["ready"]],
                                 "notReadyAddresses": [{"ip": p["ip"], "targetRef": {"name": n}} for n, p in self.pods.items() if not p["ready"]]}]}
        if "/events" in path:
            return {"items": []}
        raise AssertionError(path)

    def pod_call(self, ip, path, method="GET", body=None, timeout=1.5):
        name = next(n for n, p in self.pods.items() if p["ip"] == ip)
        self.calls.append((name, method, path, body))
        if path == "/info":
            return self.pods[name]["info"]
        if path == "/control/reset":
            self.pods[name]["info"].update(liveness_failure_injected=False, readiness_failure_injected=False, healthz_status=200)
            return {}
        if path == "/control/liveness":
            self.pods[name]["info"].update(liveness_failure_injected=True, healthz_status=500)
            return {}
        if path == "/control/readiness":
            self.pods[name]["info"].update(readiness_failure_injected=True)
            return {}
        raise AssertionError(path)


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.fc = FakeCluster()
        for target, repl in (("k8s", self.fc.k8s), ("pod_call", self.fc.pod_call)):
            p = mock.patch.object(server, target, repl); p.start(); self.addCleanup(p.stop)
        server.DEMO = server.DemoMode()
        server.DEMO.enabled, server.DEMO.next_at, server.DEMO.interval, server.DEMO.hold = True, 0, 60, 40
        self.demo = server.DEMO
        self.c = server.app.test_client()

    def inject_calls(self):
        return [c for c in self.fc.calls if c[2] in ("/control/liveness", "/control/readiness")]

    # ---- status API
    def test_status_reports_pods_probes_endpoints_and_student_app(self):
        d = self.c.get("/api/status").get_json()
        self.assertEqual(d["overall"], "HEALTHY")
        self.assertEqual(d["totals"]["healthy"], 3)
        self.assertEqual(len(d["endpoints"]["ready"]), 3)
        self.assertEqual(d["student_app"]["students"], 42)
        self.assertEqual(d["student_app"]["database_ok_pods"], 3)
        self.assertEqual(d["pods"][0]["startup"]["state"], "Passing")
        self.assertIn("startup", d["deployment"]["probes"])
        self.assertIn("demo", d)

    def test_status_reflects_a_not_ready_pod(self):
        self.fc.pods["health-demo-abc-1"]["ready"] = False
        d = self.c.get("/api/status").get_json()
        self.assertEqual((d["overall"], d["totals"]["ready"], d["totals"]["not_ready"]), ("DEGRADED", 2, 1))
        self.assertEqual(len(d["endpoints"]["not_ready"]), 1)

    # ---- demo mode: injection + safety
    def test_injects_one_failure_with_expiry_and_alternates_kinds(self):
        self.demo.tick(now=100)
        calls = self.inject_calls()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], "/control/liveness")
        self.assertEqual(calls[0][3]["duration_seconds"], server.DemoMode.LIVENESS_EXPIRY)    # self-clearing
        self.assertIsNotNone(self.demo.active)
        self.demo.tick(now=102)                              # still active -> never a second injection
        self.assertEqual(len(self.inject_calls()), 1)
        self.assertEqual(self.demo.next_kind, "readiness")

    def test_never_injects_when_disabled(self):
        self.demo.enabled = False
        self.demo.tick(now=100)
        self.assertEqual(self.inject_calls(), [])

    def test_skips_when_not_everything_is_healthy(self):
        self.fc.pods["health-demo-abc-2"]["ready"] = False
        self.demo.tick(now=100)
        self.assertEqual(self.inject_calls(), [])
        self.assertIn("health-demo-abc-2", self.demo.last_skip["reason"])

    def test_skips_during_slow_startup_scenario_or_manual_failure(self):
        self.fc.startup_delay = 30
        self.demo.tick(now=100)
        self.assertIn("slow start-up", self.demo.last_skip["reason"])
        self.fc.startup_delay = 0
        self.fc.pods["health-demo-abc-0"]["info"]["readiness_failure_injected"] = True
        self.demo.next_at = 0
        self.demo.tick(now=200)
        self.assertEqual(self.inject_calls(), [])

    # ---- demo mode: detection + recovery tracking
    def test_liveness_failure_detected_and_recovered(self):
        self.demo.tick(now=100)
        name = self.demo.active["pod"]
        pod = self.fc.pods[name]
        pod["restarts"] = 1                                   # kubelet restarted the container ...
        pod["info"].update(liveness_failure_injected=False, healthz_status=200)    # ... fresh process, clean flags
        self.demo.tick(now=118)
        self.assertIsNone(self.demo.active)
        ev = self.demo.history[0]
        self.assertEqual((ev["outcome"], ev["kind"], ev["pod"]), ("recovered", "liveness", name))
        self.assertEqual(ev["recover_seconds"], 18.0)
        self.assertEqual((self.demo.injected_total, self.demo.recovered_total), (1, 1))
        self.assertEqual(self.demo.next_at, 118 + 60)         # cool-down before the next one

    def test_readiness_failure_detected_cleared_and_recovered(self):
        self.demo.next_kind = "readiness"
        self.demo.tick(now=100)
        name = self.demo.active["pod"]
        self.fc.pods[name]["ready"] = False                  # kubelet marked it NotReady
        self.demo.tick(now=115)
        self.assertEqual(self.demo.active["state"].split(" ")[0], "detected")
        self.demo.tick(now=141)                              # hold (40 s) elapsed -> dashboard clears the failure
        self.assertIn((name, "POST", "/control/reset", {}), self.fc.calls)
        self.fc.pods[name]["ready"] = True                   # readiness probe passes again
        self.demo.tick(now=147)
        self.assertEqual(self.demo.history[0]["outcome"], "recovered")
        self.assertIsNone(self.demo.active)

    def test_unrecovered_failure_is_force_cleared(self):
        self.demo.tick(now=100)
        name = self.demo.active["pod"]
        self.demo.tick(now=100 + server.DemoMode.LIVENESS_EXPIRY + 50)       # nothing recovered, timeout passed
        self.assertIn("force-cleared", self.demo.history[0]["outcome"])
        self.assertIn((name, "POST", "/control/reset", {}), self.fc.calls)
        self.assertIsNone(self.demo.active)

    def test_replaced_pod_aborts_event_cleanly(self):
        self.demo.tick(now=100)
        del self.fc.pods[self.demo.active["pod"]]
        self.demo.tick(now=110)
        self.assertIn("aborted", self.demo.history[0]["outcome"])

    # ---- demo API
    def test_demo_api_validation_and_toggle(self):
        self.assertEqual(self.c.post("/api/demo", json={"interval": 5}).status_code, 400)
        self.assertEqual(self.c.post("/api/demo", json={"interval": "x"}).status_code, 400)
        r = self.c.post("/api/demo", json={"enabled": False, "interval": 90})
        self.assertEqual(r.status_code, 200)
        self.assertEqual((r.get_json()["enabled"], r.get_json()["interval_seconds"]), (False, 90))
        self.assertTrue(self.c.post("/api/demo/run-now").get_json()["ok"])
        self.demo.tick()                                      # run-now works even while paused
        self.assertEqual(len(self.inject_calls()), 1)

    def test_manual_actions_still_present(self):
        self.assertEqual(self.c.post("/api/action/liveness-fail", json={}).status_code, 400)      # needs a pod
        self.assertEqual(self.c.post("/api/action/restore", json={}).status_code, 200)
        self.assertEqual(self.c.post("/api/action/nope", json={}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
