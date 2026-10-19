"""Live dashboards, schedules, history and logs"""
import datetime as dt
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("monitor", __name__)

# ---------- monitoring ----------
@bp.get("/api/live")
@need("admin", "hod", "teacher", "student")
def live(u):
    lv = lectures(u, "l.status='LIVE'", tail="ORDER BY d.name,c.name,l.start_time")
    late = [] if u["role"] == "student" else [x for x in lectures(u, "l.status='SCHEDULED' AND l.date=?", (now().strftime("%Y-%m-%d"),)) if x["phase"] == "late"]
    return jsonify(live=lv, late=late, now=now().strftime("%H:%M"))

@bp.get("/api/upcoming")
@need("admin", "hod", "teacher", "student")
def upcoming(u):
    return jsonify(lectures(u, "l.status IN ('SCHEDULED','LIVE') AND l.date>=?", (now().strftime("%Y-%m-%d"),), "ORDER BY l.date,l.start_time LIMIT 100"))

@bp.get("/api/history")
@need("admin", "hod", "teacher", "student")
def history(u):
    return jsonify(lectures(u, "l.status IN ('COMPLETED','CANCELLED','MISSED')", tail="ORDER BY l.date DESC,l.start_time DESC LIMIT 200"))

@bp.get("/api/logs")
@need("root", "admin", "hod")
def logs(u):
    w, a = {"root": ("1", None), "admin": ("g.college_id=?", u["college_id"]), "hod": ("g.dept_id=?", u["dept_id"])}[u["role"]]
    sql = f"""SELECT g.ts,g.event,g.detail,g.lecture_id,COALESCE(a.name,'System') actor,COALESCE(c.code,'') college FROM logs g
      LEFT JOIN users a ON a.id=g.actor_id LEFT JOIN colleges c ON c.id=g.college_id WHERE {w} ORDER BY g.id DESC LIMIT 300"""
    return jsonify(q(sql, (a,) if a is not None else ()))

