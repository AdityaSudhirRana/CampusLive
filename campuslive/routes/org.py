"""College structure: departments, HODs, teachers"""
import datetime as dt
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("org", __name__)

# ---------- admin: departments + HODs ----------
@bp.get("/api/depts")
@need("admin")
def depts(u):
    return jsonify(q("""SELECT d.id,d.name,(SELECT name FROM users WHERE dept_id=d.id AND role='hod') hod,
      (SELECT username FROM users WHERE dept_id=d.id AND role='hod') hod_login,
      (SELECT id FROM users WHERE dept_id=d.id AND role='hod') hod_id, (SELECT active FROM users WHERE dept_id=d.id AND role='hod') hod_active,
      (SELECT COUNT(*) FROM users WHERE dept_id=d.id AND role='teacher') teachers,
      (SELECT COUNT(*) FROM lectures WHERE dept_id=d.id AND status='LIVE') live FROM depts d WHERE college_id=?""", (u["college_id"],)))

@bp.post("/api/depts")
@need("admin")
def new_dept(u):
    d = body("name", "hod_name", "username", "password")
    if q("SELECT 1 FROM depts WHERE college_id=? AND name=?", (u["college_id"], d["name"]), one=True): raise ValueError("Department already exists")
    if q("SELECT 1 FROM users WHERE username=?", (d["username"],), one=True): raise ValueError("That username is taken")
    did = ex("INSERT INTO depts(college_id,name) VALUES(?,?)", (u["college_id"], d["name"]))
    add_user("hod", d, u["college_id"], did, name_key="hod_name")
    log((u["college_id"], did), u["id"], "HOD_CREATED", detail=f"{d['name']}: {d['hod_name']}")
    publish(u["college_id"]); return jsonify(ok=1)

# ---------- HOD: teachers ----------
@bp.get("/api/teachers")
@need("admin", "hod")
def teachers(u):
    w, a = ("u.college_id=?", u["college_id"]) if u["role"] == "admin" else ("u.dept_id=?", u["dept_id"])
    return jsonify(q(f"""SELECT u.id,u.name,u.username,u.active,u.email,u.phone,d.name dept,
      (SELECT class_name||' · '||subject||' · Room '||room FROM (SELECT l.subject,l.room,c.name class_name FROM lectures l JOIN classes c ON c.id=l.class_id
        WHERE l.teacher_id=u.id AND l.status='LIVE' LIMIT 1)) live_now
      FROM users u JOIN depts d ON d.id=u.dept_id WHERE u.role='teacher' AND {w} ORDER BY d.name,u.name""", (a,)))

@bp.post("/api/teachers")
@need("hod")
def new_teacher(u):
    d = body("name", "username", "password")
    add_user("teacher", d, u["college_id"], u["dept_id"])
    log((u["college_id"], u["dept_id"]), u["id"], "TEACHER_CREATED", detail=d["name"])
    publish(u["college_id"]); return jsonify(ok=1)

