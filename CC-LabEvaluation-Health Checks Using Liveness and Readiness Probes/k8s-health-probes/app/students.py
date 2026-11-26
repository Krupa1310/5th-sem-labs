"""
Student Management - persistent SQLite storage + REST API (Flask blueprint).

This module contains ONLY the ordinary business endpoints (/api/students...).
The Kubernetes health endpoints (/healthz, /ready, /startupz, /info, /control/*)
live in app.py and are deliberately kept separate from CRUD.

Persistence: one SQLite file (DB_PATH, default /data/students.db). In Kubernetes
/data is a PersistentVolumeClaim, so records survive container restarts, pod
restarts and rollouts. SQLite needs no username/password, so there are no
database credentials to leak.

Concurrency: several pods share the same file. Reads use short connections with
a busy timeout; every write runs inside BEGIN IMMEDIATE, so two pods writing at
the same moment simply queue up instead of failing.
"""
import os
import re
import sqlite3
from contextlib import contextmanager

from flask import Blueprint, jsonify, request

bp = Blueprint("students", __name__, url_prefix="/api/students")

DEPARTMENTS = None  # free text on purpose (any department name is accepted)
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
STUDENT_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{3,20}$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    department  TEXT    NOT NULL,
    semester    INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


class ApiError(Exception):
    def __init__(self, status, message, fields=None):
        super().__init__(message)
        self.status, self.message, self.fields = status, message, fields or {}


def db_path():
    # Read at call time so tests (and operators) can change DB_PATH.
    return os.getenv("DB_PATH", "/data/students.db")


def connect(timeout=5.0):
    conn = sqlite3.connect(db_path(), timeout=timeout, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def read_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def write_tx():
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def init_db():
    """Create the folder and table if needed (safe to run from every pod)."""
    folder = os.path.dirname(db_path())
    if folder:
        os.makedirs(folder, exist_ok=True)
    with write_tx() as c:
        c.execute(SCHEMA)


def check_db(timeout=1.0):
    """Cheap connectivity check used by the READINESS probe. Returns (ok, error)."""
    try:
        conn = connect(timeout=timeout)
        try:
            conn.execute("SELECT count(*) FROM students").fetchone()
        finally:
            conn.close()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)
    except OSError as e:
        return False, str(e)


def count_students():
    try:
        with read_conn() as c:
            return c.execute("SELECT count(*) FROM students").fetchone()[0]
    except (sqlite3.Error, OSError):
        return None


# ------------------------------------------------------------- validation
def validate(data, partial_from=None):
    """Validate a student payload. With partial_from (existing row) missing fields keep their old value."""
    if not isinstance(data, dict):
        raise ApiError(400, "Request body must be a JSON object.")
    base = dict(partial_from) if partial_from else {}
    merged = {k: data.get(k, base.get(k)) for k in ("student_id", "name", "email", "department", "semester")}
    errors, clean = {}, {}

    def text(field, label, lo, hi):
        v = merged[field]
        if not isinstance(v, str) or not v.strip():
            errors[field] = f"{label} is required."
            return
        v = " ".join(v.split())
        if not lo <= len(v) <= hi:
            errors[field] = f"{label} must be {lo}-{hi} characters."
            return
        clean[field] = v

    text("student_id", "Student ID", 3, 20)
    if "student_id" in clean and not STUDENT_ID_RE.match(clean["student_id"]):
        errors["student_id"] = "Student ID may contain only letters, digits, '-' and '_' (3-20 characters)."
        clean.pop("student_id")
    if "student_id" in clean:
        clean["student_id"] = clean["student_id"].upper()
    text("name", "Name", 2, 100)
    text("email", "Email", 5, 120)
    if "email" in clean:
        if EMAIL_RE.match(clean["email"]):
            clean["email"] = clean["email"].lower()
        else:
            errors["email"] = "Enter a valid email address."
            clean.pop("email")
    text("department", "Department", 2, 60)

    sem = merged["semester"]
    if isinstance(sem, bool) or sem is None or (isinstance(sem, str) and not sem.strip()):
        errors["semester"] = "Semester is required."
    else:
        try:
            sem_i = int(sem)
            if isinstance(sem, float) and sem != sem_i:
                raise ValueError
            if not 1 <= sem_i <= 8:
                raise ValueError
            clean["semester"] = sem_i
        except (TypeError, ValueError):
            errors["semester"] = "Semester must be a whole number from 1 to 8."
    if errors:
        raise ApiError(400, "Validation failed.", errors)
    return clean


def row_dict(r):
    return {k: r[k] for k in r.keys()}


def _integrity_message(e):
    m = str(e)
    if "students.student_id" in m:
        return {"student_id": "A student with this Student ID already exists."}
    if "students.email" in m:
        return {"email": "A student with this email already exists."}
    return {}


def _parse_id(sid):
    return sid  # route converter already guarantees int


# ------------------------------------------------------------- error handling
@bp.errorhandler(ApiError)
def _api_error(e):
    body = {"error": e.message}
    if e.fields:
        body["fields"] = e.fields
    return jsonify(body), e.status


@bp.errorhandler(sqlite3.IntegrityError)
def _integrity(e):
    fields = _integrity_message(e)
    return jsonify(error=next(iter(fields.values()), "Data conflicts with an existing record."), fields=fields), 409


@bp.errorhandler(sqlite3.OperationalError)
def _operational(e):
    # 'database is locked', disk problems, missing file ...
    return jsonify(error="Database is temporarily unavailable. Please retry."), 503


# ------------------------------------------------------------- routes
@bp.get("")
def list_students():
    q = (request.args.get("q") or "").strip()
    try:
        limit = max(1, min(int(request.args.get("limit", 500)), 500))
    except ValueError:
        raise ApiError(400, "limit must be a number.")
    sql, args = "SELECT * FROM students", []
    if q:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        sql += (" WHERE student_id LIKE ? ESCAPE '\\' OR name LIKE ? ESCAPE '\\'"
                " OR email LIKE ? ESCAPE '\\' OR department LIKE ? ESCAPE '\\'")
        args = [like] * 4
        if q.isdigit():
            sql += " OR semester = ?"
            args.append(int(q))
    sql += " ORDER BY name COLLATE NOCASE, id LIMIT ?"
    args.append(limit)
    with read_conn() as c:
        rows = [row_dict(r) for r in c.execute(sql, args).fetchall()]
    return jsonify(count=len(rows), query=q, students=rows)


@bp.post("")
def add_student():
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError(400, "Request body must be valid JSON.")
    s = validate(data)
    with write_tx() as c:
        cur = c.execute(
            "INSERT INTO students (student_id, name, email, department, semester) VALUES (?,?,?,?,?)",
            (s["student_id"], s["name"], s["email"], s["department"], s["semester"]))
        row = c.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(row_dict(row)), 201


@bp.get("/<int:sid>")
def get_student(sid):
    with read_conn() as c:
        row = c.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    if row is None:
        raise ApiError(404, "Student not found.")
    return jsonify(row_dict(row))


@bp.put("/<int:sid>")
def update_student(sid):
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError(400, "Request body must be valid JSON.")
    with write_tx() as c:
        old = c.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
        if old is None:
            raise ApiError(404, "Student not found.")
        s = validate(data, partial_from=row_dict(old))
        c.execute("UPDATE students SET student_id=?, name=?, email=?, department=?, semester=?, "
                  "updated_at=datetime('now') WHERE id=?",
                  (s["student_id"], s["name"], s["email"], s["department"], s["semester"], sid))
        row = c.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    return jsonify(row_dict(row))


@bp.delete("/<int:sid>")
def delete_student(sid):
    with write_tx() as c:
        cur = c.execute("DELETE FROM students WHERE id = ?", (sid,))
        if cur.rowcount == 0:
            raise ApiError(404, "Student not found.")
    return jsonify(deleted=sid)
