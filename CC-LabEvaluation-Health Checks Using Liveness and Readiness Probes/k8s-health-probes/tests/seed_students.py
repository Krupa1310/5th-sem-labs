#!/usr/bin/env python3
"""Add sample students through the REST API (handy before a demo). Safe to re-run: duplicates are skipped.
    python tests/seed_students.py                      # http://localhost:30080
    python tests/seed_students.py http://localhost:5000
"""
import json
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:30080").rstrip("/")
CSE, ECE, ME = "Computer Science and Engineering", "Electronics and Communication", "Mechanical Engineering"
SAMPLE = [
    ("01FE23BCS001", "Srujana K", "srujana@example.com", CSE, 5), ("01FE23BCS002", "Meera Rao", "meera.rao@example.com", CSE, 5),
    ("01FE23BCS014", "Karthik Naik", "karthik.naik@example.com", CSE, 5), ("01FE23BCS027", "Ananya Hegde", "ananya.hegde@example.com", CSE, 3),
    ("01FE23BEC005", "Arun Kumar", "arun.kumar@example.com", ECE, 3), ("01FE23BEC019", "Divya Patil", "divya.patil@example.com", ECE, 5),
    ("01FE23BME003", "Rahul Desai", "rahul.desai@example.com", ME, 7), ("01FE23BME021", "Sneha Joshi", "sneha.joshi@example.com", ME, 1),
]

added = skipped = 0
for sid, name, email, dept, sem in SAMPLE:
    body = json.dumps({"student_id": sid, "name": name, "email": email, "department": dept, "semester": sem}).encode()
    req = urllib.request.Request(BASE + "/api/students", data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        added += 1
    except urllib.error.HTTPError as e:
        if e.code == 409:
            skipped += 1
        else:
            sys.exit(f"FAILED for {sid}: HTTP {e.code} {e.read().decode()[:200]}")
    except OSError as e:
        sys.exit(f"Cannot reach {BASE}: {e}")
print(f"added {added}, already present {skipped}. Open {BASE}/")
