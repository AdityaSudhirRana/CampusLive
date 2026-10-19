"""Accounts, substitutions and room changes"""
import datetime as dt
import re
from flask import Blueprint, request, session, jsonify, Response
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish
from .auth import me_json

bp = Blueprint("manage", __name__)


def target(u, uid):
    t = q("SELECT * FROM users WHERE id=?", (uid,), one=True)
    ok = t and t["id"] != u["id"] and (
        (u["role"] == "admin" and t["college_id"] == u["college_id"] and t["role"] in ("hod", "teacher")) or
        (u["role"] == "hod" and t["dept_id"] == u["dept_id"] and t["role"] == "teacher"))
    if not ok: raise ValueError("You can't manage that account")
    return t


@bp.post("/api/users/<int:uid>/active")
@need("admin", "hod")
def set_active(u, uid):
    t = target(u, uid); on = 1 if str(body().get("active")) in ("1", "true") else 0
    ex("UPDATE users SET active=? WHERE id=?", (on, uid))
    log((u["college_id"], t["dept_id"]), u["id"], "ACCOUNT_ACTIVATED" if on else "ACCOUNT_DEACTIVATED", detail=t["name"])
    publish(u["college_id"]); return jsonify(ok=1)


@bp.post("/api/users/<int:uid>/password")
@need("admin", "hod")
def reset_password(u, uid):
    t = target(u, uid); d = body("password")
    if len(d["password"]) < 6: raise ValueError("Password must be at least 6 characters")
    ex("UPDATE users SET pw=? WHERE id=?", (gph(d["password"]), uid))
    log((u["college_id"], t["dept_id"]), u["id"], "PASSWORD_RESET", detail=t["name"])
    return jsonify(ok=1)


@bp.post("/api/me/password")
@need()
def my_password(u):
    d = body("old", "new")
    if not cph(u["pw"], d["old"]): raise ValueError("Your current password is wrong")
    if len(d["new"]) < 6: raise ValueError("Password must be at least 6 characters")
    ex("UPDATE users SET pw=? WHERE id=?", (gph(d["new"]), u["id"]))
    return jsonify(ok=1)


def lecture_for(u, lid):
    l = q("SELECT * FROM lectures WHERE id=?", (lid,), one=True)
    if not l or l["college_id"] != u["college_id"]: raise ValueError("Lecture not found")
    if u["role"] == "teacher" and l["teacher_id"] != u["id"]: raise ValueError("That isn't your lecture")
    if u["role"] == "hod" and l["dept_id"] != u["dept_id"]: raise ValueError("That lecture belongs to another department")
    return l


@bp.post("/api/lectures/<int:lid>/substitute")
@need("hod")
def substitute(u, lid):
    l = lecture_for(u, lid); d = body("teacher_id")
    if l["status"] != "SCHEDULED": raise ValueError("Only a lecture that hasn't started can be reassigned")
    t = q("SELECT * FROM users WHERE id=? AND role='teacher' AND dept_id=? AND active=1", (d["teacher_id"], u["dept_id"]), one=True)
    if not t: raise ValueError("Choose an active teacher from your department")
    if t["id"] == l["teacher_id"]: raise ValueError("That teacher is already assigned")
    clash = conflict(l["college_id"], t["id"], "", l["date"], l["start_time"], l["end_time"])
    if clash: raise ValueError(clash)
    orig = l["orig_teacher_id"] or l["teacher_id"]
    ex("UPDATE lectures SET teacher_id=?, orig_teacher_id=? WHERE id=?", (t["id"], None if orig == t["id"] else orig, lid))
    log((l["college_id"], l["dept_id"]), u["id"], "LECTURE_SUBSTITUTED", lid, f"{l['subject']} is now taught by {t['name']}")
    publish(l["college_id"]); return jsonify(ok=1)


@bp.post("/api/lectures/<int:lid>/room")
@need("teacher", "hod")
def change_room(u, lid):
    l = lecture_for(u, lid); d = body("room")
    if l["status"] not in ("SCHEDULED", "LIVE"): raise ValueError("This lecture is already over")
    if q("SELECT 1 FROM lectures WHERE college_id=? AND room=? AND status='LIVE' AND id!=?", (l["college_id"], d["room"], lid), one=True):
        raise ValueError(f"Room {d['room']} already has a live lecture")
    ex("UPDATE lectures SET room=? WHERE id=?", (d["room"], lid))
    log((l["college_id"], l["dept_id"]), u["id"], "LECTURE_ROOM_CHANGED", lid, f"{l['subject']}: room {l['room']} to {d['room']}")
    publish(l["college_id"]); return jsonify(ok=1)


@bp.post("/api/me/profile")
@need()
def my_profile(u):
    d = body("name")
    email, phone = (d.get("email") or "").strip(), (d.get("phone") or "").strip()
    if len(d["name"]) > 80: raise ValueError("That name is too long")
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email): raise ValueError("That email address doesn't look right")
    if phone and not re.match(r"^[0-9+()\-\s]{7,20}$", phone): raise ValueError("Use digits, spaces, + or - for the phone number")
    ex("UPDATE users SET name=?, email=?, phone=? WHERE id=?", (d["name"], email or None, phone or None, u["id"]))
    return me_json(cur())
