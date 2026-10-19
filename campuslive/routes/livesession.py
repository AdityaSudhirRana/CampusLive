"""Live session: student check-in with the teacher's class code, and lecture detail"""
import datetime as dt
from flask import Blueprint, request, session, jsonify, Response
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("livesession", __name__)


@bp.post("/api/lectures/<int:lid>/checkin")
@need("student")
def checkin(u, lid):
    d = body("code")
    l = q("SELECT * FROM lectures WHERE id=? AND class_id=? AND status='LIVE'", (lid, u["class_id"]), one=True)
    if not l: raise ValueError("That lecture isn't live for your class")
    if d["code"] != l["code"]: raise ValueError("That code isn't right. The teacher can see it on their lecture")
    ex("INSERT OR IGNORE INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)", (lid, u["id"], now().isoformat(timespec="seconds")))
    publish(l["college_id"]); return jsonify(ok=1)


@bp.get("/api/lectures/<int:lid>/detail")
@need("admin", "hod", "teacher")
def detail(u, lid):
    rows = lectures(u, "l.id=?", (lid,))
    if not rows: raise ValueError("Lecture not found")
    present = q("SELECT s.name, a.ts FROM attendance a JOIN users s ON s.id=a.student_id WHERE a.lecture_id=? ORDER BY a.ts", (lid,))
    events = q("SELECT g.ts,g.event,g.detail,COALESCE(a.name,'System') actor FROM logs g LEFT JOIN users a ON a.id=g.actor_id WHERE g.lecture_id=? ORDER BY g.id", (lid,))
    return jsonify(lecture=rows[0], present=present, events=events)
