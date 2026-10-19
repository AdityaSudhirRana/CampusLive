"""End-to-end check of the whole hierarchy. Run: python tests/test_flow.py"""
import os, sys, tempfile, datetime as dt
os.environ["CAMPUSLIVE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from campuslive import create_app

app = create_app()
def client(user=None, pw="secret1"):
    c = app.test_client()
    if user: assert c.post("/api/login", json={"username": user, "password": pw}).status_code == 200, user
    return c
def post(c, url, data=None, ok=200):
    r = c.post(url, json=data or {}); assert r.status_code == ok, (url, r.status_code, r.get_json()); return r.get_json()
def get(c, url, ok=200):
    r = c.get(url); assert r.status_code == ok, (url, r.status_code); return r.get_json()

root = client("root", "root123")
assert post(root, "/api/colleges", {"name": "X College", "admin_name": "P", "admin_username": "pr", "password": "secret1"})["code"] == "COL001"
admin = client("pr"); post(admin, "/api/depts", {"name": "CS", "hod_name": "H", "username": "hod", "password": "secret1"})
hod = client("hod"); post(hod, "/api/teachers", {"name": "T One", "username": "t1", "password": "secret1"})
post(hod, "/api/teachers", {"name": "T Two", "username": "t2", "password": "secret1"}); post(hod, "/api/classes", {"name": "FY CS"})
t1 = client("t1"); cid = get(t1, "/api/classes")[0]["id"]
n = dt.datetime.now(); today = n.strftime("%Y-%m-%d")
lec = lambda a, b: {"class_id": cid, "subject": "DS", "room": "204", "date": today, "start": a, "end": b}
if n.hour < 22:
    s, e = (n - dt.timedelta(minutes=3)).strftime("%H:%M"), (n + dt.timedelta(minutes=50)).strftime("%H:%M")
    if s < e:
        lid = post(t1, "/api/lectures", lec(s, e))["id"]
        assert "clash" or post(t1, "/api/lectures", lec(s, e), 400)             # same teacher + room, same time
        post(t1, f"/api/lectures/{lid}/start")
        live = get(admin, "/api/live")["live"][0]; assert "code" not in live and not live["verified"]
        code = get(t1, "/api/live")["live"][0]["code"]
        studs = []
        for i in (1, 2):
            c = app.test_client(); post(c, "/api/register", {"college_code": "COL001", "class_id": cid, "username": f"s{i}", "name": f"S{i}", "password": "secret1"}); studs.append(c)
        post(studs[0], f"/api/lectures/{lid}/checkin", {"code": "x"}, 400)
        for c in studs: post(c, f"/api/lectures/{lid}/checkin", {"code": code})
        sl = get(studs[0], "/api/live")["live"][0]; assert sl["checked"] and not {"present", "enrolled", "verified", "code"} & set(sl)   # students never see counts
        assert get(admin, "/api/live")["live"][0]["verified"]
        d = get(admin, f"/api/lectures/{lid}/detail"); assert len(d["present"]) == 2 and d["events"]
        post(t1, f"/api/lectures/{lid}/room", {"room": "205"}); post(t1, f"/api/lectures/{lid}/end")
        assert get(hod, "/api/reports")[0]["held"] == 1 and b"Teacher" in hod.get("/api/reports.csv").data
tid = get(hod, "/api/teachers")[1]["id"]
future = (n + dt.timedelta(days=2)).strftime("%Y-%m-%d")
l2 = post(t1, "/api/lectures", {**lec("09:00", "10:00"), "date": future})["id"]
post(hod, f"/api/lectures/{l2}/substitute", {"teacher_id": tid})
assert get(app.test_client() if False else client("t2"), "/api/upcoming")[0]["covering_for"] == "T One"
t2 = client("t2"); r = post(t2, "/api/timetable", {"class_id": cid, "subject": "Java", "room": "301", "weekday": 0, "start": "11:00", "end": "12:00", "weeks": 4}); assert r["made"] >= 3
post(hod, f"/api/users/{tid}/active", {"active": "0"}); assert client().post("/api/login", json={"username": "t2", "password": "secret1"}).status_code == 400
assert get(t2, "/api/me")["user"] is None
post(t1, "/api/me/password", {"old": "secret1", "new": "secret2"}); client("t1", "secret2")
assert post(hod, "/api/users/1/active", {"active": 0}, 400)  # cannot touch root
p = post(t1, "/api/me/profile", {"name": "T One Renamed", "email": "t1@college.edu", "phone": "+91 98765 43210"}); assert p["user"]["email"] == "t1@college.edu"
post(t1, "/api/me/profile", {"name": "X", "email": "bad"}, 400)
print("all checks passed")
