"""Weekly timetable: one slot generates the lectures for the coming weeks"""
import datetime as dt
from flask import Blueprint, request, session, jsonify, Response
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("timetable", __name__)


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@bp.get("/api/timetable")
@need("teacher", "hod")
def slots(u):
    w, a = ("t.teacher_id=?", u["id"]) if u["role"] == "teacher" else ("t.dept_id=?", u["dept_id"])
    rows = q(f"SELECT t.*, c.name class_name, p.name teacher FROM timetable t JOIN classes c ON c.id=t.class_id "
             f"JOIN users p ON p.id=t.teacher_id WHERE {w} ORDER BY t.weekday, t.start_time", (a,))
    for r in rows: r["day"] = DAYS[r["weekday"]]
    return jsonify(rows)


@bp.post("/api/timetable")
@need("teacher")
def new_slot(u):
    d = body("class_id", "subject", "room", "weekday", "start", "end", "weeks")
    try:
        assert mins(d["end"]) > mins(d["start"]); wd = int(d["weekday"]); weeks = max(1, min(12, int(d["weeks"]))); assert 0 <= wd <= 6
    except Exception: raise ValueError("Check the day and times, and make sure the end time is after the start time")
    if not q("SELECT 1 FROM classes WHERE id=? AND dept_id=?", (d["class_id"], u["dept_id"]), one=True): raise ValueError("Unknown class")
    sid = ex("INSERT INTO timetable(college_id,dept_id,class_id,teacher_id,subject,room,weekday,start_time,end_time) VALUES(?,?,?,?,?,?,?,?,?)",
             (u["college_id"], u["dept_id"], d["class_id"], u["id"], d["subject"], d["room"], wd, d["start"], d["end"]))
    n, today = now(), dt.date.today(); made, skipped = 0, []
    for i in range(weeks * 7):
        day = today + dt.timedelta(days=i)
        if day.weekday() != wd or (day == today and n.hour * 60 + n.minute >= mins(d["end"])): continue
        date = day.isoformat()
        why = conflict(u["college_id"], u["id"], d["room"], date, d["start"], d["end"])
        if why: skipped.append(why); continue
        ex("INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,timetable_id) VALUES(?,?,?,?,?,?,?,?,?,?)",
           (u["college_id"], u["dept_id"], d["class_id"], u["id"], d["subject"], d["room"], date, d["start"], d["end"], sid)); made += 1
    log((u["college_id"], u["dept_id"]), u["id"], "TIMETABLE_CREATED", detail=f"{d['subject']} every {DAYS[wd]} {d['start']}-{d['end']}: {made} lectures scheduled")
    publish(u["college_id"]); return jsonify(made=made, skipped=len(skipped), reasons=skipped[:3])


@bp.post("/api/timetable/<int:sid>/delete")
@need("teacher")
def delete_slot(u, sid):
    s = q("SELECT * FROM timetable WHERE id=? AND teacher_id=?", (sid, u["id"]), one=True)
    if not s: raise ValueError("Timetable slot not found")
    ex("DELETE FROM lectures WHERE timetable_id=? AND status='SCHEDULED' AND date>=?", (sid, dt.date.today().isoformat()))
    ex("DELETE FROM timetable WHERE id=?", (sid,))
    log((u["college_id"], u["dept_id"]), u["id"], "TIMETABLE_REMOVED", detail=s["subject"])
    publish(u["college_id"]); return jsonify(ok=1)
