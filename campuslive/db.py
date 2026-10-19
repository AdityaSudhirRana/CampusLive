"""SQLite access and schema."""
import sqlite3
from werkzeug.security import generate_password_hash as gph
from .config import DB, ROOT_USER, ROOT_PASSWORD

SCHEMA = """
CREATE TABLE IF NOT EXISTS colleges(id INTEGER PRIMARY KEY, code TEXT UNIQUE, name TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS depts(id INTEGER PRIMARY KEY, college_id INT, name TEXT, UNIQUE(college_id,name));
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, role TEXT, username TEXT UNIQUE, name TEXT, pw TEXT,
  college_id INT, dept_id INT, class_id INT);
CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, college_id INT, dept_id INT, name TEXT, UNIQUE(dept_id,name));
CREATE TABLE IF NOT EXISTS lectures(id INTEGER PRIMARY KEY, college_id INT, dept_id INT, class_id INT, teacher_id INT,
  subject TEXT, room TEXT, date TEXT, start_time TEXT, end_time TEXT, status TEXT DEFAULT 'SCHEDULED',
  started_at TEXT, ended_at TEXT);
CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, ts TEXT, college_id INT, dept_id INT, actor_id INT,
  event TEXT, lecture_id INT, detail TEXT);
"""

def conn():
    c = sqlite3.connect(DB, timeout=10); c.row_factory = sqlite3.Row; return c

def q(sql, a=(), one=False):
    c = conn()
    try:
        r = c.execute(sql, a).fetchall(); c.commit()
        r = [dict(x) for x in r]
        return (r[0] if r else None) if one else r
    finally: c.close()

def ex(sql, a=()):
    c = conn()
    try:
        cur = c.execute(sql, a); c.commit(); return cur.lastrowid
    finally: c.close()

EXTRA = """
CREATE TABLE IF NOT EXISTS attendance(lecture_id INT, student_id INT, ts TEXT, PRIMARY KEY(lecture_id, student_id));
CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY, college_id INT, dept_id INT, class_id INT, teacher_id INT,
  subject TEXT, room TEXT, weekday INT, start_time TEXT, end_time TEXT);
"""

def migrate(c):
    """Adds newer tables/columns so databases from earlier versions keep working."""
    c.executescript(EXTRA)
    def add(table, col, ddl):
        if col not in [r[1] for r in c.execute(f"PRAGMA table_info({table})")]:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
    add("users", "active", "INT DEFAULT 1")
    add("users", "email", "TEXT")
    add("users", "phone", "TEXT")
    add("lectures", "code", "TEXT")
    add("lectures", "orig_teacher_id", "INT")
    add("lectures", "timetable_id", "INT")


def init_db():
    c = conn(); c.execute("PRAGMA journal_mode=WAL"); c.executescript(SCHEMA); migrate(c); c.commit(); c.close()
    if not q("SELECT 1 FROM users WHERE role='root'"):
        ex("INSERT INTO users(role,username,name,pw) VALUES('root',?,?,?)",
           (ROOT_USER, "Root Admin", gph(ROOT_PASSWORD)))

