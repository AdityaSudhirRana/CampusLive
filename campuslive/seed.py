"""
High-fidelity demo dataset based on the official Sheth L.U.J. and Sir M.V. College
Second Year Computer Science Semester III Lecture & Lab Timetable (A.Y. 2026-2027).
Configured strictly with actual faculty members and student profiles.
"""
import datetime as dt
from werkzeug.security import generate_password_hash as gph
from .db import q, ex, conn
from .helpers import add_user, now, log

def seed(force=False):
    if not force and q("SELECT 1 FROM colleges WHERE name LIKE '%Sheth%'"):
        return False
    
    # Clear existing data for a clean, accurate setup
    c = conn()
    for tbl in ["attendance", "logs", "lectures", "timetable", "classes", "depts", "users", "colleges"]:
        c.execute(f"DELETE FROM {tbl}")
    c.commit()
    c.close()

    n = now()
    today = n.strftime("%Y-%m-%d")
    hm = lambda t: t.strftime("%H:%M")

    # 1. Root Admin
    ex("INSERT INTO users(role,username,name,pw,active) VALUES('root','root','Root Admin',?,1)", (gph("root123"),))

    # 2. College
    cid = ex("INSERT INTO colleges(code,name,created_at) VALUES('COL001','Sheth L.U.J. and Sir M.V. College',?)",
             (n.isoformat(timespec="seconds"),))

    # 3. Principal (Admin)
    add_user("admin", {"username": "principal", "name": "Dr. Principal", "password": "demo123"}, cid)
    ex("UPDATE users SET email='principal@mvlu.edu.in', phone='+91 98200 11111' WHERE username='principal'")

    # 4. Department (Single focused Computer Science Department)
    did_cs = ex("INSERT INTO depts(college_id,name) VALUES(?, 'Computer Science')", (cid,))

    # 5. Classes across all three academic tiers
    cls_fycs = ex("INSERT INTO classes(college_id,dept_id,name) VALUES(?,?,'FY B.Sc. CS')", (cid, did_cs))
    cls_sycs = ex("INSERT INTO classes(college_id,dept_id,name) VALUES(?,?,'SY B.Sc. CS')", (cid, did_cs))
    cls_tycs = ex("INSERT INTO classes(college_id,dept_id,name) VALUES(?,?,'TY B.Sc. CS')", (cid, did_cs))

    # 6. Core Faculty Members Only (No dummy/unrelated teachers)
    # Head of Department: Asst. Prof. Pradnya Kharade
    tid_pradnya = add_user("hod", {"username": "pradnya_k", "name": "Asst. Prof. Pradnya Kharade", "password": "demo123"}, cid, did_cs)
    ex("UPDATE users SET email='pradnya.kharade@mvlu.edu.in', phone='+91 98203 34567' WHERE id=?", (tid_pradnya,))

    # Faculty & Project Guide: Asst. Prof. Rohit Sahu
    tid_rohit = add_user("teacher", {"username": "rohit_sahu", "name": "Asst. Prof. Rohit Sahu", "password": "demo123"}, cid, did_cs)
    ex("UPDATE users SET email='rohit.sahu@mvlu.edu.in', phone='+91 98201 12345' WHERE id=?", (tid_rohit,))

    # Faculty & Course Coordinator: Asst. Prof. Jyoti Chauhan
    tid_jyoti = add_user("teacher", {"username": "jyoti_chauhan", "name": "Asst. Prof. Jyoti Chauhan", "password": "demo123"}, cid, did_cs)
    ex("UPDATE users SET email='jyoti.chauhan@mvlu.edu.in', phone='+91 98202 23456' WHERE id=?", (tid_jyoti,))

    # 7. Real Students (Only the requested real student profiles)
    student_records = [
        ("student", "Aditya Rana", "S105", "ranaadityacs252612@gmail.com", "+91 98765 43210"),
        ("mohi_pathan", "Mohi Pathan", "S106", "mohi.pathan@student.mvlu.edu.in", "+91 98765 43211"),
        ("suraj", "Suraj", "S107", "suraj@student.mvlu.edu.in", "+91 98765 43212"),
        ("dhruv_choubey", "Dhruv Choubey", "S108", "dhruv.choubey@student.mvlu.edu.in", "+91 98765 43213"),
        ("akshat_halwai", "Akshat Halwai", "S109", "akshat.halwai@student.mvlu.edu.in", "+91 98765 43214"),
    ]

    student_ids = []
    for uname, sname, roll, semail, sphone in student_records:
        sid = add_user("student", {"username": uname, "name": sname, "password": "demo123"}, cid, did_cs, cls_sycs)
        ex("UPDATE users SET email=?, phone=? WHERE id=?", (semail, sphone, sid))
        student_ids.append(sid)

    # Secondary class students for FY and TY so live check-in works across all tiers
    fy_student = add_user("student", {"username": "student_fy", "name": "Student FY (CS)", "password": "demo123"}, cid, did_cs, cls_fycs)
    ty_student = add_user("student", {"username": "student_ty", "name": "Student TY (CS)", "password": "demo123"}, cid, did_cs, cls_tycs)

    # 8. Official Timetable Slots for SY B.Sc. CS (Faithfully mapped to our 3 core faculty)
    official_slots = [
        # Monday
        (0, "07:30", "08:30", "Hindi Bhasha Vyavaharik Prayog", "Room 209", tid_pradnya),
        (0, "08:30", "09:30", "Principles of Operating Systems", "Room 209", tid_jyoti),
        (0, "09:30", "10:30", "Java Programming", "Room 209", tid_rohit),
        (0, "10:50", "11:50", "Principles of Operating Systems Practical", "Room 209", tid_jyoti),
        (0, "11:50", "13:50", "Scala for DS Practical", "IT Lab", tid_pradnya),
        (0, "13:50", "15:50", "Principles of Operating Systems Practical", "IT Lab", tid_jyoti),

        # Tuesday
        (1, "07:30", "09:30", "Co-Curricular Sports Training & Tests", "Room 209", tid_pradnya),
        (1, "09:30", "10:30", "Principles of Operating Systems", "Room 209", tid_jyoti),
        (1, "10:50", "11:50", "Fintech Start up", "Room 206", tid_pradnya),
        (1, "11:50", "12:50", "Library / Self Study", "Library", tid_jyoti),
        (1, "12:50", "13:50", "Field Project", "Room 209", tid_jyoti),

        # Wednesday
        (2, "09:30", "10:30", "Theory of Computation", "Room 209", tid_pradnya),
        (2, "10:50", "11:50", "Data Structures", "Room 209", tid_rohit),
        (2, "11:50", "12:50", "Fintech Start up", "Room 209", tid_pradnya),
        (2, "12:50", "13:50", "Python for Data Science Practical", "Room 209", tid_jyoti),

        # Thursday
        (3, "07:30", "08:30", "Hindi Bhasha Vyavaharik Prayog", "Room 208", tid_pradnya),
        (3, "08:30", "09:30", "Data Structures", "Room 003", tid_rohit),
        (3, "09:30", "10:30", "Java Programming", "Room 003", tid_rohit),
        (3, "10:50", "11:50", "Theory of Computation", "Room 003", tid_pradnya),
        (3, "11:50", "13:50", "Python for Data Science Practical", "IT Lab", tid_jyoti),

        # Friday
        (4, "07:30", "09:30", "Data Structures Practical", "IT Lab", tid_rohit),
        (4, "09:30", "10:30", "Data Structures Practical", "Room 209", tid_rohit),
        (4, "10:50", "11:50", "Field Project", "Room 003", tid_rohit),

        # Saturday
        (5, "07:30", "09:30", "Java Programming Practical", "IT Lab", tid_rohit),
        (5, "09:30", "10:30", "Java Programming Practical", "Room 003", tid_rohit),
        (5, "10:50", "11:50", "Scala for DS Practical", "Room 003", tid_pradnya),
    ]

    for wd, start, end, sub, room, tid in official_slots:
        ex("INSERT INTO timetable(college_id,dept_id,class_id,teacher_id,subject,room,weekday,start_time,end_time) VALUES(?,?,?,?,?,?,?,?,?)",
           (cid, did_cs, cls_sycs, tid, sub, room, wd, start, end))

    # 9. Active Live Lectures Across ALL THREE Classes (FY, SY, TY) with ALL Teachers Occupied!
    # Session 1 (SY B.Sc. CS): Data Structures Practical in IT Lab by Asst. Prof. Rohit Sahu
    live_start_sy = n - dt.timedelta(minutes=25)
    live_end_sy = n + dt.timedelta(minutes=35)
    lid_sy = ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status,code,started_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_sycs, tid_rohit, "Data Structures Practical", "IT Lab", today, hm(live_start_sy), hm(live_end_sy),
         "LIVE", "4821", (live_start_sy + dt.timedelta(minutes=1)).isoformat(timespec="seconds"))
    )
    log((cid, did_cs), tid_rohit, "LECTURE_STARTED", lid_sy, "Data Structures Practical in IT Lab")

    # Mark all 5 real students present in the SY live practical!
    for sid in student_ids:
        ex("INSERT INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)",
           (lid_sy, sid, (live_start_sy + dt.timedelta(minutes=2)).isoformat(timespec="seconds")))

    # Session 2 (FY B.Sc. CS): Principles of Operating Systems in Room 209 by Asst. Prof. Jyoti Chauhan
    live_start_fy = n - dt.timedelta(minutes=18)
    live_end_fy = n + dt.timedelta(minutes=42)
    lid_fy = ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status,code,started_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_fycs, tid_jyoti, "Principles of Operating Systems", "Room 209", today, hm(live_start_fy), hm(live_end_fy),
         "LIVE", "3891", (live_start_fy + dt.timedelta(minutes=2)).isoformat(timespec="seconds"))
    )
    log((cid, did_cs), tid_jyoti, "LECTURE_STARTED", lid_fy, "Principles of Operating Systems in Room 209")
    ex("INSERT INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)", (lid_fy, fy_student, (live_start_fy + dt.timedelta(minutes=3)).isoformat(timespec="seconds")))
    # Add check-ins from students to verify the lecture
    for sid in student_ids[:3]:
        ex("INSERT OR IGNORE INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)",
           (lid_fy, sid, (live_start_fy + dt.timedelta(minutes=4)).isoformat(timespec="seconds")))

    # Session 3 (TY B.Sc. CS): Theory of Computation in Room 003 by Asst. Prof. Pradnya Kharade (HOD)
    live_start_ty = n - dt.timedelta(minutes=12)
    live_end_ty = n + dt.timedelta(minutes=48)
    lid_ty = ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status,code,started_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_tycs, tid_pradnya, "Theory of Computation", "Room 003", today, hm(live_start_ty), hm(live_end_ty),
         "LIVE", "6724", (live_start_ty + dt.timedelta(minutes=1)).isoformat(timespec="seconds"))
    )
    log((cid, did_cs), tid_pradnya, "LECTURE_STARTED", lid_ty, "Theory of Computation in Room 003")
    ex("INSERT INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)", (lid_ty, ty_student, (live_start_ty + dt.timedelta(minutes=3)).isoformat(timespec="seconds")))
    for sid in student_ids[:3]:
        ex("INSERT OR IGNORE INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)",
           (lid_ty, sid, (live_start_ty + dt.timedelta(minutes=4)).isoformat(timespec="seconds")))

    # Session 4: Upcoming Scheduled Lecture Today
    up_start = n + dt.timedelta(minutes=45)
    up_end = n + dt.timedelta(minutes=105)
    ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_sycs, tid_rohit, "Java Programming", "Room 206", today, hm(up_start), hm(up_end), "SCHEDULED")
    )

    # Session 5: Late Lecture Alert ("Due but not started" for Principal overview)
    late_start = n - dt.timedelta(minutes=15)
    late_end = n + dt.timedelta(minutes=45)
    ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_sycs, tid_pradnya, "Fintech Start up", "Room 208", today, hm(late_start), hm(late_end), "SCHEDULED")
    )

    # Session 6: Future Lecture with Substitution (Asst. Prof. Rohit Sahu covering for Asst. Prof. Jyoti Chauhan)
    future_date = (n + dt.timedelta(days=2)).strftime("%Y-%m-%d")
    lid_sub = ex(
        "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,orig_teacher_id,subject,room,date,start_time,end_time,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (cid, did_cs, cls_sycs, tid_rohit, tid_jyoti, "Field Project", "Room 209", future_date, "12:50", "13:50", "SCHEDULED")
    )
    log((cid, did_cs), tid_pradnya, "LECTURE_SUBSTITUTED", lid_sub, "Asst. Prof. Rohit Sahu covering for Asst. Prof. Jyoti Chauhan")

    # 10. Completed Historical Lectures (Over past 20 days) with ONLY real student attendee names
    historical_subjects = [
        ("Java Programming", "Room 209", tid_rohit, "09:30", "10:30"),
        ("Data Structures", "Room 003", tid_rohit, "08:30", "09:30"),
        ("Data Structures Practical", "IT Lab", tid_rohit, "07:30", "09:30"),
        ("Java Programming Practical", "IT Lab", tid_rohit, "07:30", "09:30"),
        ("Field Project", "Room 003", tid_rohit, "10:50", "11:50"),
        ("Principles of Operating Systems", "Room 209", tid_jyoti, "08:30", "09:30"),
        ("Principles of Operating Systems Practical", "IT Lab", tid_jyoti, "13:50", "15:50"),
        ("Python for Data Science Practical", "IT Lab", tid_jyoti, "11:50", "13:50"),
        ("Theory of Computation", "Room 209", tid_pradnya, "09:30", "10:30"),
        ("Fintech Start up", "Room 206", tid_pradnya, "10:50", "11:50"),
        ("Scala for DS Practical", "IT Lab", tid_pradnya, "11:50", "13:50"),
    ]

    for day_offset in range(1, 20):
        past_dt = n - dt.timedelta(days=day_offset)
        if past_dt.weekday() >= 6:  # Skip Sundays
            continue
        past_date_str = past_dt.strftime("%Y-%m-%d")

        sub_info = historical_subjects[day_offset % len(historical_subjects)]
        s_title, s_room, s_tid, s_start, s_end = sub_info
        status = "COMPLETED"

        if day_offset == 8:
            status = "CANCELLED"

        actual_start = f"{past_date_str}T{s_start}:00" if status == "COMPLETED" else None
        actual_end = f"{past_date_str}T{s_end}:00" if status == "COMPLETED" else None

        hid = ex(
            "INSERT INTO lectures(college_id,dept_id,class_id,teacher_id,subject,room,date,start_time,end_time,status,code,started_at,ended_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cid, did_cs, cls_sycs, s_tid, s_title, s_room, past_date_str, s_start, s_end,
             status, "4821" if status == "COMPLETED" else None, actual_start, actual_end)
        )

        if status == "COMPLETED":
            # Attendance: ONLY the 5 real students (Aditya Rana, Mohi Pathan, Suraj, Dhruv Choubey, Akshat Halwai)
            for sid in student_ids:
                ex("INSERT INTO attendance(lecture_id,student_id,ts) VALUES(?,?,?)",
                   (hid, sid, f"{past_date_str}T{s_start}:05"))
            log((cid, did_cs), s_tid, "LECTURE_STARTED", hid, s_title)
            log((cid, did_cs), s_tid, "LECTURE_ENDED", hid, s_title)
        elif status == "CANCELLED":
            log((cid, did_cs), s_tid, "LECTURE_CANCELLED", hid, f"{s_title}: Department Activity")

    return True
