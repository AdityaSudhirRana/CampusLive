"""Teacher: classes and the lecture lifecycle"""
import datetime as dt
import random
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("teaching", __name__)

# ---------- teacher: classes + lectures ----------
@bp.get("/api/classes")
@need("teacher", "hod")
def classes(u):
    return jsonify(q("SELECT id,name FROM classes WHERE dept_id=? ORDER BY name", (u["dept_id"],)))

@bp.post("/api/classes")
@need("teacher", "hod")
def new_class(u):
    d = body("name")
    if q("SELECT 1 FROM classes WHERE dept_id=? AND name=?", (u["dept_id"], d["name"]), one=True): raise ValueError("That class already exists")
    ex("INSERT INTO classes(college_id,dept_id,name) VALUES(?,?,?)", (u["college_id"], u["dept_id"], d["name"]))
    return jsonify(ok=1)

@bp.post("/api/lectures")
@need("teacher")
def new_lecture(u):
    d = body("class_id", "subject", "room", "date", "start", "end")
    try: dt.date.fromisoformat(d["date"]); assert mins(d["end"]) > mins(d["start"])
    except Exception: raise ValueError("Check the date, and make sure the end time is after the start time")
    if not q("SELECT 1 FROM classes WHERE id=? AND dept_id=?", (d["class_id"], u["dept_id"]), one=True): raise ValueError("Unknown class")
    clash = conflict(u["college_id"], u["id"], d["room"], d["date"], d["start"], d["end"])
    if clash: raise ValueError(clash)
    lid = ex("""INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time) VALUES(?,?,?,?,?,?,?,?,?)""",
             (u["college_id"], u["dept_id"], d["class_id"], u["id"], d["subject"], d["room"], d["date"], d["start"], d["end"]))
    log((u["college_id"], u["dept_id"]), u["id"], "LECTURE_SCHEDULED", lid, f"{d['subject']} {d['date']} {d['start']}-{d['end']} Room {d['room']}")
    publish(u["college_id"]); return jsonify(id=lid)

@bp.post("/api/lectures/<int:lid>/<act>")
@need("teacher")
def lecture_act(u, lid, act):
    l = q("SELECT * FROM lectures WHERE id=? AND teacher_id=?", (lid, u["id"]), one=True)
    if not l: raise ValueError("Lecture not found")
    ids = (l["college_id"], l["dept_id"]); stamp = now().isoformat(timespec="seconds")
    if act == "start":
        p = phase(l)
        if p not in ("available", "late"):
            raise ValueError(f"You can make a lecture live from {EARLY} minutes before its start until its end time")
        if q("SELECT 1 FROM lectures WHERE teacher_id=? AND status='LIVE'", (u["id"],), one=True): raise ValueError("You already have a live lecture. End it first")
        clash = q("SELECT 1 FROM lectures WHERE college_id=? AND room=? AND status='LIVE'", (l["college_id"], l["room"]), one=True)
        if clash: raise ValueError(f"Room {l['room']} already has a live lecture")
        ex("UPDATE lectures SET status='LIVE', started_at=?, code=? WHERE id=?", (stamp, '%04d' % random.randint(0, 9999), lid)); log(ids, u["id"], "LECTURE_STARTED", lid, f"{l['subject']} (scheduled {l['start_time']})")
    elif act == "end" and l["status"] == "LIVE":
        ex("UPDATE lectures SET status='COMPLETED', ended_at=? WHERE id=?", (stamp, lid)); log(ids, u["id"], "LECTURE_ENDED", lid, l["subject"])
    elif act == "cancel" and l["status"] == "SCHEDULED":
        ex("UPDATE lectures SET status='CANCELLED' WHERE id=?", (lid,)); log(ids, u["id"], "LECTURE_CANCELLED", lid, l["subject"])
    else: raise ValueError("That action isn't available for this lecture")
    publish(l["college_id"]); return jsonify(ok=1)

