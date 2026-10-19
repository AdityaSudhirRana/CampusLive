"""Root admin: colleges"""
import datetime as dt
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("root", __name__)

# ---------- root admin ----------
@bp.get("/api/colleges")
@need("root")
def colleges(u):
    return jsonify(q("""SELECT c.*, (SELECT COUNT(*) FROM depts WHERE college_id=c.id) depts,
      (SELECT COUNT(*) FROM users WHERE college_id=c.id AND role='teacher') teachers,
      (SELECT COUNT(*) FROM lectures WHERE college_id=c.id AND status='LIVE') live,
      (SELECT COUNT(*) FROM lectures WHERE college_id=c.id) total,
      (SELECT name FROM users WHERE college_id=c.id AND role='admin' LIMIT 1) admin FROM colleges c ORDER BY id"""))

@bp.post("/api/colleges")
@need("root")
def new_college(u):
    d = body("name", "admin_name", "admin_username", "password")
    n = (q("SELECT COUNT(*) n FROM colleges", one=True)["n"]) + 1
    code = "COL%03d" % n
    d["username"] = d["admin_username"]
    if q("SELECT 1 FROM users WHERE username=?", (d["username"],), one=True): raise ValueError("That username is taken")
    cid = ex("INSERT INTO colleges(code,name,created_at) VALUES(?,?,?)", (code, d["name"], now().isoformat(timespec="seconds")))
    add_user("admin", {**d, "name": d["admin_name"]}, cid)
    log((cid, None), u["id"], "COLLEGE_CREATED", detail=f"{code} {d['name']}")
    publish(0); return jsonify(code=code)

