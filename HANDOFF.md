# CampusLive handoff

Paste this file plus ALL_SOURCE.txt into a new session to continue.

## Product idea (from the owner)
One platform where teachers, HODs and the principal create, operate and monitor lectures. The core
is the LIVE lecture: a teacher makes a lecture live, and the principal can see it is officially being
held now. Hierarchy: Root Admin > College > Principal > HOD > Teacher > Class/Lecture > Live session > Logs.
Owner prefers: multi-file projects, a design that does not look generic, full summary plus source when
a session nears its limit.

## Stack
Python 3, Flask, SQLite (file campuslive.db), Server-Sent Events for live updates, plain JS frontend
(no build step, classic scripts sharing globals). Start with `python run.py --demo`.

## Done
- v3 (UI pass): landing page before sign-in (hash routes #signin, #signup), pop-up dialogs for every create/edit/confirm form (MODALS registry in views.js), three-dot row menus, page headers with primary action buttons, navy/blue professional palette, editable profile (name, email, phone via POST /api/me/profile), students see Present/Absent only (attendance counts and verification are stripped server-side for students).
- Roles and permissions: root, admin (principal), hod, teacher, student. Root creates colleges (COL001...).
  Principal creates departments + HODs. HOD creates teachers and classes. Students self-register with
  the college code and class.
- Lecture lifecycle: SCHEDULED > LIVE > COMPLETED, plus CANCELLED and MISSED ("not held").
  Go live window: 10 min before start until end. One live lecture per teacher and per room.
  Forgotten lectures auto-end 15 min after scheduled end (sweeper). All steps are logged.
- Official verification: starting a lecture generates a 4-digit class code, visible only to the teacher.
  Students enter it to mark themselves present. 2+ check-ins shows "Verified by students".
- Live board for principal/HOD (grouped by department, elapsed timer, verification, late lectures),
  student board with check-in, lecture detail modal with timeline and attendee names.
- Weekly timetable: a slot generates lectures for up to 12 weeks, skipping room/teacher clashes.
  Clash checking also applies to single lectures.
- HOD: substitute teacher on an unstarted lecture, room change. Teacher: room change.
- Account management: admin/HOD deactivate/reactivate and reset passwords; everyone can change their own.
- Reports per teacher (held, not held, cancelled, held rate, average start delay, average attendance)
  for 7/30/90 days, with CSV download.
- Real-time: SSE per college (`/api/stream`); dashboards re-fetch on each ping, plus 30 s fallback.
- Tests: tests/test_flow.py covers the whole flow. Demo data: campuslive/seed.py.

## Not done (suggested order)
1. Edit/delete for classes, lectures, departments; student management (list, remove, move class).
2. Announcements from principal/HOD to a department or college, shown on boards.
3. Principal drill-down College > Department > Class > Lecture > Teacher pages; room occupancy view.
4. Rate-limit check-in attempts (4-digit code can be guessed); optional time-limited code rotation.
5. Notifications when a lecture goes live (web push / email); reconnect catch-up indicator.
6. Daily/weekly analytics charts; log retention and filters; Root admin per-college usage stats.
7. Production: gunicorn (single worker for SSE or Redis pub/sub), PostgreSQL, HTTPS, CSRF, real SECRET_KEY.

## API summary (JSON, session cookie auth)
Auth: POST /api/login, /api/logout, /api/register; GET /api/me; GET /api/public/classes?code=
Root: GET/POST /api/colleges
Admin: GET/POST /api/depts; GET /api/teachers
HOD: POST /api/teachers; GET/POST /api/classes (teacher too); POST /api/lectures/<id>/substitute
Teacher: POST /api/lectures; POST /api/lectures/<id>/start|end|cancel; POST /api/lectures/<id>/room;
         GET/POST /api/timetable; POST /api/timetable/<id>/delete
Student: POST /api/lectures/<id>/checkin {code}
Monitoring: GET /api/live, /api/upcoming, /api/history, /api/logs, /api/lectures/<id>/detail,
            /api/reports?days=, /api/reports.csv?days=; stream: GET /api/stream
Accounts: POST /api/users/<id>/active, /api/users/<id>/password, /api/me/password

## Code map
run.py (port fallback, browser) | campuslive/__init__.py (factory) | config.py (EARLY, GRACE, VERIFY_MIN)
db.py (schema + migrate) | helpers.py (phase, need, body, lectures, conflict) | realtime.py | sweeper.py
routes/: auth, root, org, teaching, monitor, manage, timetable, livesession, reports
static/js: util (helpers, api, builders) render (renderers) board views (tabs + MODALS) landing (home, sign-in) app (shell, dialogs, menus, events)
Adding a screen: add an endpoint, a renderer in R (render.js), a page(...) in TABS (views.js). Adding a form: add an entry to MODALS and an openBtn(...) or menu item with data-open.
