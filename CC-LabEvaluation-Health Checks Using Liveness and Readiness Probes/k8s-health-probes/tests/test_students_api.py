"""CRUD, search and validation tests for the Student Management API (no Kubernetes needed).
Run:  python -m unittest discover -s tests -v"""
import os
import sqlite3
import unittest

import _helpers  # noqa: F401  (sets sys.path)
import students
from app import app as flask_app, db_state


def good(**over):
    d = {"student_id": "01FE23BCS001", "name": "Srujana K", "email": "Srujana@Example.com",
         "department": "Computer Science and Engineering", "semester": 5}
    d.update(over)
    return d


class StudentApiTests(unittest.TestCase):
    def setUp(self):
        self.path = _helpers.fresh_db()
        students.init_db()
        db_state["initialised"] = True
        self.c = flask_app.test_client()

    # ---- create / read
    def test_add_and_get(self):
        r = self.c.post("/api/students", json=good())
        self.assertEqual(r.status_code, 201)
        s = r.get_json()
        self.assertEqual(s["student_id"], "01FE23BCS001")
        self.assertEqual(s["email"], "srujana@example.com")           # normalised
        got = self.c.get(f"/api/students/{s['id']}")
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.get_json()["name"], "Srujana K")

    def test_list_all(self):
        self.c.post("/api/students", json=good())
        self.c.post("/api/students", json=good(student_id="S02", name="Arun", email="arun@x.com", semester=3))
        d = self.c.get("/api/students").get_json()
        self.assertEqual(d["count"], 2)
        self.assertEqual([s["name"] for s in d["students"]], ["Arun", "Srujana K"])   # sorted by name

    # ---- search
    def test_search(self):
        self.c.post("/api/students", json=good())
        self.c.post("/api/students", json=good(student_id="ECE001", name="Arun Kumar", email="arun@x.com",
                                               department="Electronics", semester=3))
        def names(q):
            return [s["name"] for s in self.c.get("/api/students", query_string={"q": q}).get_json()["students"]]
        self.assertEqual(names("arun"), ["Arun Kumar"])               # by name (case-insensitive)
        self.assertEqual(names("ece001"), ["Arun Kumar"])             # by student id
        self.assertEqual(names("electronics"), ["Arun Kumar"])        # by department
        self.assertEqual(names("example.com"), ["Srujana K"])         # by email
        self.assertEqual(names("5"), ["Srujana K"])                   # by semester
        self.assertEqual(names("zzz"), [])
        self.assertEqual(len(names("%")), 0)                          # wildcard characters are escaped
        self.assertEqual(len(names("_")), 0)

    # ---- update
    def test_update(self):
        sid = self.c.post("/api/students", json=good()).get_json()["id"]
        r = self.c.put(f"/api/students/{sid}", json={"name": "New Name", "semester": 6})
        self.assertEqual(r.status_code, 200)
        s = r.get_json()
        self.assertEqual((s["name"], s["semester"], s["department"]), ("New Name", 6, good()["department"]))
        self.assertEqual(self.c.put("/api/students/9999", json={"name": "Nobody"}).status_code, 404)
        self.assertEqual(self.c.put(f"/api/students/{sid}", json={"semester": 12}).status_code, 400)

    # ---- delete
    def test_delete(self):
        sid = self.c.post("/api/students", json=good()).get_json()["id"]
        self.assertEqual(self.c.delete(f"/api/students/{sid}").status_code, 200)
        self.assertEqual(self.c.get(f"/api/students/{sid}").status_code, 404)
        self.assertEqual(self.c.delete(f"/api/students/{sid}").status_code, 404)

    # ---- validation + duplicates
    def test_validation_errors(self):
        for bad, field in [(good(name=""), "name"), (good(email="not-an-email"), "email"),
                           (good(semester=0), "semester"), (good(semester="abc"), "semester"),
                           (good(semester=True), "semester"), (good(student_id="a b"), "student_id"),
                           (good(department=" "), "department")]:
            r = self.c.post("/api/students", json=bad)
            self.assertEqual(r.status_code, 400, bad)
            self.assertIn(field, r.get_json()["fields"], bad)
        self.assertEqual(self.c.post("/api/students", data="not json", content_type="application/json").status_code, 400)
        self.assertEqual(self.c.post("/api/students", json=[1, 2]).status_code, 400)
        self.assertEqual(self.c.get("/api/students").get_json()["count"], 0)          # nothing was stored

    def test_duplicates_rejected(self):
        self.assertEqual(self.c.post("/api/students", json=good()).status_code, 201)
        r = self.c.post("/api/students", json=good(email="other@x.com"))
        self.assertEqual((r.status_code, list(r.get_json()["fields"])), (409, ["student_id"]))
        r = self.c.post("/api/students", json=good(student_id="NEW1"))
        self.assertEqual((r.status_code, list(r.get_json()["fields"])), (409, ["email"]))

    def test_sql_injection_is_just_text(self):
        self.c.post("/api/students", json=good(name="Robert'); DROP TABLE students;--"))
        self.assertEqual(self.c.get("/api/students").get_json()["count"], 1)
        self.assertEqual(self.c.get("/api/students", query_string={"q": "' OR 1=1 --"}).get_json()["count"], 0)

    # ---- persistence
    def test_data_survives_new_connection_and_new_app_process_state(self):
        """Simulates a container restart: all in-memory state is gone, the file remains."""
        self.c.post("/api/students", json=good())
        db_state["initialised"] = False
        students.init_db()                                  # what a restarted container does at boot
        self.assertEqual(self.c.get("/api/students").get_json()["count"], 1)
        raw = sqlite3.connect(self.path).execute("SELECT name FROM students").fetchall()
        self.assertEqual(raw, [("Srujana K",)])

    def test_api_errors_are_json(self):
        r = self.c.get("/api/students/abc")
        self.assertEqual((r.status_code, r.is_json), (404, True))
        r = self.c.patch("/api/students")
        self.assertEqual((r.status_code, r.is_json), (405, True))

    def test_database_unavailable_returns_503(self):
        os.environ["DB_PATH"] = "/nonexistent-dir-xyz/students.db"
        r = self.c.get("/api/students")
        self.assertEqual(r.status_code, 503)
        self.assertIn("error", r.get_json())


if __name__ == "__main__":
    unittest.main()
