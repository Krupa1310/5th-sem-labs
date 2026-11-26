"""Offline consistency checks between the Kubernetes YAML, the Dockerfiles, the scripts and the Flask code.
These do NOT replace deploying to a cluster - they catch typos (wrong image tag, wrong probe path, missing volume ...)."""
import os
import re
import unittest

import _helpers  # noqa: F401
from app import app as flask_app

try:
    import yaml
except ImportError:          # pragma: no cover
    yaml = None

ROOT = _helpers.ROOT


def load(name):
    with open(os.path.join(ROOT, "k8s", name), encoding="utf-8") as f:
        return list(yaml.safe_load_all(f))


def text(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


@unittest.skipIf(yaml is None, "PyYAML not installed (pip install pyyaml)")
class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.dep = load("deployment.yaml")[0]
        self.pod = self.dep["spec"]["template"]["spec"]
        self.ctr = self.pod["containers"][0]
        self.svc = load("service.yaml")[0]
        self.pvc = load("pvc.yaml")[0]
        self.dash_dep, self.dash_svc = load("dashboard.yaml")
        rbac = load("dashboard-rbac.yaml")
        self.role = next(d for d in rbac if d["kind"] == "Role")

    def test_existing_names_and_ports_are_preserved(self):
        self.assertEqual(self.dep["metadata"]["name"], "health-demo")
        self.assertEqual(self.dep["spec"]["replicas"], 3)
        self.assertEqual((self.svc["metadata"]["name"], self.svc["spec"]["ports"][0]["nodePort"]), ("health-demo-svc", 30080))
        self.assertEqual((self.dash_dep["metadata"]["name"], self.dash_svc["metadata"]["name"]), ("health-dashboard", "health-dashboard"))
        self.assertEqual(self.dash_svc["spec"]["ports"][0]["nodePort"], 30090)

    def test_image_names_match_dockerfile_build_commands(self):
        for script in ("scripts/deploy.ps1", "scripts/deploy.sh"):
            t = text(script)
            self.assertIn(self.ctr["image"], t, script)
            self.assertIn(self.dash_dep["spec"]["template"]["spec"]["containers"][0]["image"], t, script)
            self.assertRegex(t, r"docker build -t \S+\s+app", script)
            self.assertRegex(t, r"docker build -t \S+\s+dashboard", script)
            self.assertNotIn(":1.0", t, script)           # no stale tags left behind

    def test_probes_use_real_get_routes_and_the_container_port(self):
        get_routes = {r.rule for r in flask_app.url_map.iter_rules() if "GET" in r.methods}
        port = self.ctr["ports"][0]["containerPort"]
        for kind in ("startupProbe", "livenessProbe", "readinessProbe"):
            probe = self.ctr[kind]
            self.assertIn(probe["httpGet"]["path"], get_routes, kind)
            self.assertEqual(probe["httpGet"]["port"], port, kind)
            for f in ("periodSeconds", "timeoutSeconds", "failureThreshold"):
                self.assertIn(f, probe, f"{kind}.{f} should be explicit")
        self.assertEqual(self.ctr["livenessProbe"]["httpGet"]["path"], "/healthz")
        self.assertEqual(self.ctr["readinessProbe"]["httpGet"]["path"], "/ready")
        self.assertEqual(self.ctr["startupProbe"]["httpGet"]["path"], "/startupz")
        # startup gets a generous window; liveness must not be more forgiving than ~30 s
        self.assertGreaterEqual(self.ctr["startupProbe"]["periodSeconds"] * self.ctr["startupProbe"]["failureThreshold"], 30)
        self.assertLessEqual(self.ctr["livenessProbe"]["periodSeconds"] * self.ctr["livenessProbe"]["failureThreshold"], 30)

    def test_pvc_is_mounted_where_the_app_writes_its_database(self):
        vol = next(v for v in self.pod["volumes"] if v["name"] == "student-data")
        self.assertEqual(vol["persistentVolumeClaim"]["claimName"], self.pvc["metadata"]["name"])
        mount = next(m for m in self.ctr["volumeMounts"] if m["name"] == "student-data")
        db_path = next(e["value"] for e in self.ctr["env"] if e["name"] == "DB_PATH")
        self.assertTrue(db_path.startswith(mount["mountPath"] + "/"), (db_path, mount))
        self.assertIn("ReadWriteOnce", self.pvc["spec"]["accessModes"])
        self.assertIn(f"ENV PYTHONUNBUFFERED=1 \\\n    DB_PATH={db_path}", text("app/Dockerfile"))

    def test_no_secrets_or_credentials_in_manifests(self):
        blob = "".join(text(f"k8s/{f}") for f in os.listdir(os.path.join(ROOT, "k8s"))).lower()
        for word in ("password", "secret", "token:", "apikey"):
            self.assertNotIn(word, blob)

    def test_service_selects_and_targets_the_deployment(self):
        labels = self.dep["spec"]["template"]["metadata"]["labels"]
        self.assertEqual(self.dep["spec"]["selector"]["matchLabels"], labels)
        self.assertEqual(self.svc["spec"]["selector"], labels)
        self.assertEqual(self.svc["spec"]["ports"][0]["targetPort"], self.ctr["ports"][0]["containerPort"])

    def test_dashboard_targets_the_student_application(self):
        env = {e["name"]: e["value"] for e in self.dash_dep["spec"]["template"]["spec"]["containers"][0]["env"]}
        self.assertEqual(env["TARGET_DEPLOYMENT"], self.dep["metadata"]["name"])
        self.assertEqual(env["TARGET_SERVICE"], self.svc["metadata"]["name"])
        k, v = env["TARGET_LABEL"].split("=")
        self.assertEqual(self.dep["spec"]["template"]["metadata"]["labels"][k], v)
        self.assertEqual(env["DEMO_MODE"], "on")
        self.assertGreaterEqual(int(env["DEMO_INTERVAL_SECONDS"]), 45)

    def test_dashboard_rbac_is_unchanged_least_privilege(self):
        rules = {(tuple(r["apiGroups"]), tuple(r["resources"])): set(r["verbs"]) for r in self.role["rules"]}
        self.assertEqual(rules[(("",), ("pods", "endpoints", "events", "services"))], {"get", "list"})
        self.assertEqual(rules[(("apps",), ("deployments",))], {"get", "list", "patch"})
        self.assertEqual(len(rules), 2)

    def test_dockerfiles_copy_every_python_module_and_static_dir(self):
        d = text("app/Dockerfile")
        for f in ("app.py", "students.py", "static"):
            self.assertIn(f, d)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "app/static/index.html")))
        self.assertIn("server.py", text("dashboard/Dockerfile"))


if __name__ == "__main__":
    unittest.main()
