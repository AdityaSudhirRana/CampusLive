"""Reports: how lectures actually went, per teacher, with CSV export"""
import datetime as dt
from flask import Blueprint, request, session, jsonify, Response
from werkzeug.security import check_password_hash as cph
from ..db import q, ex
from ..config import EARLY
from ..helpers import *
from ..realtime import publish

bp = Blueprint("reports", __name__)


import csv, io

SQL = """SELECT t.name teacher, d.name dept, COUNT(*) total,
  SUM(l.status IN ('COMPLETED','LIVE')) held, SUM(l.status='MISSED') missed, SUM(l.status='CANCELLED') cancelled,
  AVG(CASE WHEN l.started_at IS NOT NULL THEN (strftime('%s',l.started_at)-strftime('%s',l.date||'T'||l.start_time||':00'))/60.0 END) delay,
  AVG(CASE WHEN l.status IN ('COMPLETED','LIVE') THEN (SELECT COUNT(*) FROM attendance a WHERE a.lecture_id=l.id)*100.0/
      NULLIF((SELECT COUNT(*) FROM users s WHERE s.class_id=l.class_id AND s.role='student'),0) END) attendance
  FROM lectures l JOIN users t ON t.id=l.teacher_id JOIN depts d ON d.id=l.dept_id
  WHERE {w} AND l.date>=? AND l.status!='SCHEDULED' GROUP BY t.id ORDER BY d.name, t.name"""


def rows_for(u):
    days = min(365, max(1, int(request.args.get("days", 30))))
    w, a = ("l.college_id=?", u["college_id"]) if u["role"] == "admin" else ("l.dept_id=?", u["dept_id"])
    out = q(SQL.format(w=w), (a, (dt.date.today() - dt.timedelta(days=days)).isoformat()))
    for r in out:
        done = r["held"] + r["missed"]
        r["rate"] = round(r["held"] * 100 / done) if done else None
        r["delay"] = None if r["delay"] is None else round(r["delay"])
        r["attendance"] = None if r["attendance"] is None else round(r["attendance"])
    return out


@bp.get("/api/reports")
@need("admin", "hod")
def report(u): return jsonify(rows_for(u))


@bp.get("/api/reports.csv")
@need("admin", "hod")
def report_csv(u):
    out = io.StringIO(); w = csv.writer(out)
    w.writerow(["Teacher", "Department", "Scheduled", "Held", "Not held", "Cancelled", "Held rate %", "Avg start delay (min)", "Avg attendance %"])
    for r in rows_for(u):
        w.writerow([r["teacher"], r["dept"], r["total"], r["held"], r["missed"], r["cancelled"], r["rate"], r["delay"], r["attendance"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=campuslive-report.csv"})
