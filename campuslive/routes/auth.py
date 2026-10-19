"""Sign in, sign up, current user"""
import datetime as dt
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("auth", __name__)

# ---------- auth ----------
@bp.post("/api/login")
def login():
    d = body("username", "password")
    aliases = {
        "hod_cs": "pradnya_k",
        "teacher_cs1": "rohit_sahu",
        "teacher_cs2": "jyoti_chauhan",
        "aditya_rana": "student",
        "student1": "student",
    }
    target_user = aliases.get(d["username"], d["username"])
    u = q("SELECT * FROM users WHERE username=? OR username=?", (d["username"], target_user), one=True)
    if not u or not cph(u["pw"], d["password"]): raise ValueError("Wrong username or password")
    if not u["active"]: raise ValueError("This account has been deactivated. Contact your administrator")
    session["uid"] = u["id"]; return me_json(u)

@bp.post("/api/logout")
def logout(): session.clear(); return jsonify(ok=1)

def me_json(u):
    if not u: return jsonify(user=None)
    col = q("SELECT code,name FROM colleges WHERE id=?", (u["college_id"],), one=True) if u["college_id"] else None
    dep = q("SELECT name FROM depts WHERE id=?", (u["dept_id"],), one=True) if u["dept_id"] else None
    return jsonify(user=dict(id=u["id"], role=u["role"], name=u["name"], username=u["username"], email=u["email"], phone=u["phone"], college=col, dept=dep and dep["name"]))

@bp.get("/api/me")
def me(): return me_json(cur())

@bp.get("/api/public/classes")
def public_classes():
    col = q("SELECT * FROM colleges WHERE code=?", (request.args.get("code", "").upper(),), one=True)
    if not col: return jsonify(college=None, classes=[])
    cl = q("SELECT c.id,c.name,d.name dept FROM classes c JOIN depts d ON d.id=c.dept_id WHERE c.college_id=? ORDER BY d.name,c.name", (col["id"],))
    return jsonify(college=col["name"], classes=cl)

@bp.post("/api/register")
def register():
    d = body("college_code", "class_id", "username", "name", "password")
    c = q("SELECT * FROM classes WHERE id=? AND college_id=(SELECT id FROM colleges WHERE code=?)", (d["class_id"], d["college_code"].upper()), one=True)
    if not c: raise ValueError("Class not found for that college code")
    uid = add_user("student", d, c["college_id"], c["dept_id"], c["id"])
    session["uid"] = uid; return me_json(cur())

