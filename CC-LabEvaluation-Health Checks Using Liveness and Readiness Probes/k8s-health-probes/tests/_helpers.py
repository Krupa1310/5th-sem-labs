"""Shared test setup: put app/ and dashboard/ on sys.path and give every test its own temp database."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("app", "dashboard"):
    p = os.path.join(ROOT, sub)
    if p not in sys.path:
        sys.path.insert(0, p)


def fresh_db():
    """Point DB_PATH at a brand-new temp file and return the path."""
    d = tempfile.mkdtemp(prefix="students-test-")
    path = os.path.join(d, "students.db")
    os.environ["DB_PATH"] = path
    return path
