"""Shared helpers: time, lecture phase, auth guards, validation, scoping."""
import datetime as dt
from functools import wraps
from flask import request, session, jsonify
from werkzeug.security import generate_password_hash as gph
from .db import q, ex
from .config import EARLY, GRACE, VERIFY_MIN

# ---------- helpers ----------
def now(): return dt.datetime.now()
def mins(s): h, m = map(int, s.split(":")); return h * 60 + m
def log(l_or_ids, actor, event, lid=None, detail=""):
    cid, did = l_or_ids
    ex("INSERT INTO logs(ts,college_id,dept_id,actor_id,event,lecture_id,detail) VALUES(?,?,?,?,?,?,?)",
       (now().isoformat(timespec="seconds"), cid, did, actor, event, lid, detail))

def phase(l):
    if l["status"] != "SCHEDULED": return l["status"].lower()
    n = now(); today = n.strftime("%Y-%m-%d"); nm = n.hour * 60 + n.minute
    if l["date"] > today: return "scheduled"
    if l["date"] < today or nm > mins(l["end_time"]): return "missed"
    s = mins(l["start_time"])
    if nm >= s + EARLY: return "late"
    if nm >= s - EARLY: return "available"
    return "scheduled"

def cur():
    uid = session.get("uid")
    u = q("SELECT * FROM users WHERE id=?", (uid,), one=True) if uid else None
    return u if u and u["active"] else None

def need(*roles):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            u = cur()
            if not u: return jsonify(error="Not signed in"), 401
            if roles and u["role"] not in roles: return jsonify(error="You don't have access to this"), 403
            return f(u, *a, **k)
        return w
    return deco

def body(*req):
    d = request.get_json(silent=True) or {}
    d = {k: (v.strip() if isinstance(v, str) else v) for k, v in d.items()}
    miss = [r for r in req if d.get(r) in (None, "")]
    if miss: raise ValueError("Please fill in: " + ", ".join(miss))
    return d


def add_user(role, d, cid, did=None, class_id=None, name_key="name"):
    if len(d["password"]) < 6: raise ValueError("Password must be at least 6 characters")
    if q("SELECT 1 FROM users WHERE username=?", (d["username"],), one=True): raise ValueError("That username is taken")
    return ex("INSERT INTO users(role,username,name,pw,college_id,dept_id,class_id) VALUES(?,?,?,?,?,?,?)",
              (role, d["username"], d[name_key], gph(d["password"]), cid, did, class_id))

LSQL = """SELECT l.*, (SELECT COUNT(*) FROM attendance a WHERE a.lecture_id=l.id) present, (SELECT COUNT(*) FROM users s WHERE s.class_id=l.class_id AND s.role='student') enrolled, (SELECT name FROM users o WHERE o.id=l.orig_teacher_id) covering_for, t.name teacher, c.name class_name, d.name dept FROM lectures l
 JOIN users t ON t.id=l.teacher_id JOIN classes c ON c.id=l.class_id JOIN depts d ON d.id=l.dept_id"""
def scope(u):
    return {"admin": ("l.college_id=?", u["college_id"]), "hod": ("l.dept_id=?", u["dept_id"]),
            "teacher": ("l.teacher_id=?", u["id"]), "student": ("l.class_id=?", u["class_id"])}[u["role"]]
def lectures(u, where="1", args=(), tail=""):
    w, a = scope(u)
    rows = q(f"{LSQL} WHERE {w} AND {where} {tail}", (a,) + tuple(args))
    checked = set()
    if u["role"] == "student":
        checked = {x["lecture_id"] for x in q("SELECT lecture_id FROM attendance WHERE student_id=?", (u["id"],))}
    for r in rows:
        r["phase"] = phase(r)
        r["verified"] = r["present"] >= VERIFY_MIN
        r["checked"] = r["id"] in checked
        if u["role"] != "teacher":
            r.pop("code", None)          # the class code is only ever shown to the teacher
        if u["role"] == "student":
            for k in ("present", "enrolled", "verified"): r.pop(k, None)   # attendance numbers are for staff only
    return rows



def conflict(cid, teacher_id, room, date, start, end):
    """Returns a message if the teacher or room is already booked in that window, else None."""
    for r in q("SELECT teacher_id,room,subject,start_time,end_time FROM lectures WHERE college_id=? AND date=? "
               "AND status IN ('SCHEDULED','LIVE') AND start_time<? AND end_time>?", (cid, date, end, start)):
        if r["teacher_id"] == teacher_id:
            return f"That teacher already has {r['subject']} from {r['start_time']} to {r['end_time']} on {date}"
        if r["room"] == room:
            return f"Room {room} is already booked for {r['subject']} from {r['start_time']} to {r['end_time']} on {date}"
    return None
