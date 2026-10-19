# CampusLive

Real-time academic activity monitoring for colleges. Flask + SQLite, live updates over Server-Sent Events.

## Run
    pip install -r requirements.txt
    python run.py --demo        # --demo loads sample data the first time

The terminal prints the address (normally http://127.0.0.1:5000) and opens it in your browser.
If port 5000 is busy, the next free port is used automatically (`PORT=8000 python run.py` to choose).
To open it from other devices on your Wi-Fi: `HOST=0.0.0.0 python run.py`.

## Logins
| Role | User / Faculty / Student | Username | Password |
|---|---|---|---|
| Root admin | System Root | `root` | `root123` |
| Principal | Dr. Principal | `principal` | `demo123` |
| HOD Computer Science | Asst. Prof. Pradnya Kharade | `pradnya_k` (or `hod_cs`) | `demo123` |
| Faculty (Guide) | Asst. Prof. Rohit Sahu | `rohit_sahu` (or `teacher_cs1`) | `demo123` |
| Faculty (Coordinator) | Asst. Prof. Jyoti Chauhan | `jyoti_chauhan` (or `teacher_cs2`) | `demo123` |
| Student (Lead) | Aditya Rana (S105) | `student` (or `aditya_rana`) | `demo123` |
| Student | Mohi Pathan | `mohi_pathan` | `demo123` |
| Student | Suraj | `suraj` | `demo123` |
| Student | Dhruv Choubey | `dhruv_choubey` | `demo123` |
| Student | Akshat Halwai | `akshat_halwai` | `demo123` |

Demo class code for the live session in Computer Science: **4821** (Asst. Prof. Rohit Sahu sees it on his active live lecture in `IT Lab`).
Tests: `python tests/test_flow.py`. Handoff for continuing in another session: `HANDOFF.md` (all source in `ALL_SOURCE.txt`).

## Layout
    run.py                     starts the server (port fallback, browser open)
    campuslive/
      __init__.py              app factory
      config.py  db.py         settings, SQLite schema and queries
      helpers.py               time, lecture phase, permissions, validation
      realtime.py              Server-Sent Events
      sweeper.py               auto-ends forgotten lectures
      seed.py                  demo data
      routes/                  auth, root, org (depts/HODs/teachers), teaching, monitor
      templates/index.html
      static/css/app.css
      static/js/               util, render, board, views, landing, app

## Lecture rules (edit in config.py)
A teacher can go live from 10 minutes before the start until the end time. A lecture left live is
ended 15 minutes after its scheduled end. A lecture never started is marked "Not held". One live
lecture per teacher and per room. Every step is written to the activity log.
