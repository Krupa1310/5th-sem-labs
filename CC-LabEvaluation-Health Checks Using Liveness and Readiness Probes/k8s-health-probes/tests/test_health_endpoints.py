"""Tests for the Kubernetes health endpoints, which are separate from the student CRUD endpoints."""
import os
import unittest

import _helpers  # noqa: F401
import students
import app as app_module
from app import app as flask_app, db_state, flags, flag_until


class HealthEndpointTests(unittest.TestCase):
    def setUp(self):
        _helpers.fresh_db()
        students.init_db()
        db_state.update(initialised=True, error=None)
        flags["liveness_fail"] = flags["readiness_fail"] = False
        flag_until["liveness_fail"] = flag_until["readiness_fail"] = None
        app_module.STARTUP_DELAY = 0
        self.c = flask_app.test_client()

    def test_healthy_defaults(self):
        for path in ("/healthz", "/ready", "/startupz", "/whoami", "/info"):
            self.assertEqual(self.c.get(path).status_code, 200, path)

    def test_liveness_failure_injection_and_reset(self):
        self.assertEqual(self.c.post("/control/liveness", json={"fail": True}).status_code, 200)
        self.assertEqual(self.c.get("/healthz").status_code, 500)
        self.assertEqual(self.c.get("/ready").status_code, 200)            # readiness unaffected
        self.c.post("/control/reset")
        self.assertEqual(self.c.get("/healthz").status_code, 200)

    def test_crash_alias_still_works(self):
        self.c.post("/crash")
        self.assertEqual(self.c.get("/healthz").status_code, 500)

    def test_readiness_failure_injection(self):
        self.c.post("/control/readiness", json={"fail": True})
        r = self.c.get("/ready")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(self.c.get("/healthz").status_code, 200)          # liveness unaffected
        self.c.post("/control/reset")
        self.assertEqual(self.c.get("/ready").status_code, 200)

    def test_slow_startup_makes_ready_503_but_healthz_200(self):
        app_module.STARTUP_DELAY = 10_000
        self.assertEqual(self.c.get("/ready").status_code, 503)
        self.assertEqual(self.c.get("/healthz").status_code, 200)

    def test_startup_probe_waits_for_database(self):
        db_state["initialised"] = False
        self.assertEqual(self.c.get("/startupz").status_code, 503)
        self.assertEqual(self.c.get("/ready").status_code, 503)
        self.assertEqual(self.c.get("/healthz").status_code, 200)          # still alive while initialising

    def test_readiness_fails_when_database_is_unreachable_but_liveness_stays_ok(self):
        os.environ["DB_PATH"] = "/nonexistent-dir-xyz/students.db"
        r = self.c.get("/ready")
        self.assertEqual(r.status_code, 503)
        self.assertIn("database", r.get_json()["reason"])
        self.assertEqual(self.c.get("/healthz").status_code, 200)          # liveness never checks the DB

    def test_injected_failure_with_duration_clears_itself(self):
        self.c.post("/control/readiness", json={"fail": True, "duration_seconds": 30})
        self.assertEqual(self.c.get("/ready").status_code, 503)
        flag_until["readiness_fail"] = 0          # pretend the 30 s have passed
        self.assertEqual(self.c.get("/ready").status_code, 200)
        self.assertEqual(self.c.post("/control/liveness", json={"fail": True, "duration_seconds": "x"}).status_code, 400)

    def test_health_endpoints_are_not_under_the_crud_prefix(self):
        crud = {r.rule for r in flask_app.url_map.iter_rules() if r.rule.startswith("/api/students")}
        health = {"/healthz", "/ready", "/startupz", "/info", "/control/liveness", "/control/readiness", "/control/reset"}
        self.assertTrue(crud)
        self.assertFalse(health & crud)
        self.assertEqual(self.c.get("/api/students/healthz").status_code, 404)

    def test_info_reports_database_and_student_count(self):
        self.c.post("/api/students", json={"student_id": "A001", "name": "Test", "email": "t@x.com",
                                           "department": "CSE", "semester": 2})
        d = self.c.get("/info").get_json()
        self.assertTrue(d["database"]["ok"])
        self.assertEqual(d["database"]["students"], 1)
        self.assertIn("startup", d["kubelet_probe_counts"])

    def test_kubelet_probe_results_are_recorded_only_for_kube_probe_user_agent(self):
        self.c.get("/healthz", headers={"User-Agent": "kube-probe/1.30"})
        self.c.get("/healthz", headers={"User-Agent": "curl/8"})
        counts = self.c.get("/info").get_json()["kubelet_probe_counts"]["liveness"]
        self.assertEqual(counts["ok"], 1)

    def test_pod_header_and_ui(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Student Management", r.data)
        self.assertIn("X-Served-By", r.headers)


if __name__ == "__main__":
    unittest.main()
