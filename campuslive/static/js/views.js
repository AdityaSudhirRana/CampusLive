// What each role sees: tabs (pages) and the pop-up dialogs opened from them.
let STAFF = [], repDays = 30;
const ROLES = {root: "Root admin", admin: "Principal", hod: "Head of department", teacher: "Teacher", student: "Student"};
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const board = () => `<div data-src="/api/live" data-r="board"></div>`;
const classSelect = `<label>Class<select name="class_id" required data-src="/api/classes" data-r="classOpts"></select></label>`;
const PW = 'minlength="6"';

// Dialogs: key => (id) => {title, html, wide}
const MODALS = {
  college: () => ({title: "Create a college", html: formHtml("/api/colleges", [["name", "College name"], ["admin_name", "Principal's name"], ["admin_username", "Principal login"], ["password", "Password", "password", PW]], "Create college", "College created")}),
  dept: () => ({title: "Add a department", html: formHtml("/api/depts", [["name", "Department"], ["hod_name", "HOD's name"], ["username", "HOD login"], ["password", "Password", "password", PW]], "Create department", "Department created")}),
  teacher: () => ({title: "Add a teacher", html: formHtml("/api/teachers", [["name", "Teacher's name"], ["username", "Login"], ["password", "Password", "password", PW]], "Create teacher", "Teacher created")}),
  class: () => ({title: "Add a class", html: formHtml("/api/classes", [["name", "Class name, for example FY B.Sc. CS"]], "Add class", "Class added")}),
  lecture: () => ({title: "Schedule a lecture", html: `<form class="mform" data-post="/api/lectures" data-ok="Lecture scheduled">${classSelect}${fieldsHtml([["subject", "Subject"], ["room", "Room"], ["date", "Date", "date", `value="${today()}"`], ["start", "Start time", "time"], ["end", "End time", "time"]])}${foot("Schedule lecture")}</form>`}),
  slot: () => ({title: "Add a weekly slot", html: `<form class="mform" data-post="/api/timetable" data-ok="Weekly slot saved">${classSelect}${fieldsHtml([["subject", "Subject"], ["room", "Room"]])}
    <label>Day<select name="weekday">${DAYS.map((x, i) => `<option value="${i}">${x}</option>`).join("")}</select></label>${fieldsHtml([["start", "Start time", "time"], ["end", "End time", "time"], ["weeks", "Repeat for how many weeks", "number", 'min="1" max="12" value="8"']])}${foot("Create weekly slot")}</form>`}),
  room: id => ({title: "Change room", html: formHtml(`/api/lectures/${id}/room`, [["room", "New room"]], "Change room", "Room changed")}),
  sub: id => ({title: "Substitute teacher", html: `<form class="mform" data-post="/api/lectures/${id}/substitute" data-ok="Substitute assigned"><label>Teacher who will take this lecture<select name="teacher_id" required>${STAFF.filter(s => s.active).map(s => `<option value="${s.id}">${e(s.name)}</option>`).join("")}</select></label>${foot("Assign substitute")}</form>`}),
  cancel: id => ({title: "Cancel this lecture?", html: confirmHtml("Students and your HOD will see it as cancelled. This can't be undone.", `/api/lectures/${id}/cancel`, "Cancel lecture", "Lecture cancelled")}),
  ttdel: id => ({title: "Remove weekly slot?", html: confirmHtml("The slot and its future scheduled lectures will be removed. Past lectures stay in the history.", `/api/timetable/${id}/delete`, "Remove slot", "Weekly slot removed")}),
  deactivate: id => ({title: "Deactivate this account?", html: confirmHtml("They will be signed out and won't be able to sign in until you reactivate the account.", `/api/users/${id}/active`, "Deactivate", "Account deactivated", [["active", "", "hidden", "0"]])}),
  pw: id => ({title: "Reset password", html: formHtml(`/api/users/${id}/password`, [["password", "New password", "password", PW]], "Reset password", "Password reset")}),
  password: () => ({title: "Change your password", html: formHtml("/api/me/password", [["old", "Current password", "password"], ["new", "New password", "password", PW]], "Change password", "Password changed")}),
  profile: () => ({title: "Edit profile", html: formHtml("/api/me/profile", [["name", "Full name", "text", `value="${e(me.name)}" maxlength="80"`], ["email", "Email address", "email", `value="${e(me.email || "")}"`, 1], ["phone", "Phone number", "tel", `value="${e(me.phone || "")}"`, 1]], "Save changes", "Profile updated")}),
};

const account = ["Account", () => head("Account", "Your details and sign-in settings.") + `<div data-src="/api/me" data-r="profile"></div>`];
const reports = ["Reports", () => head("Reports", "How lectures actually went: held, not held, how late they started, and how many students checked in.",
  `${[7, 30, 90].map(n => `<button class="btn ${n === repDays ? "pri" : ""}" data-act="days" data-d="${n}">Last ${n} days</button>`).join("")}<a class="btn" href="/api/reports.csv?days=${repDays}">Download CSV</a>`) + plain(`/api/reports?days=${repDays}`, "report")];
const plain = (src, r) => `<section class="card"><div class="scroll" data-src="${src}" data-r="${r}"></div></section>`;
const page = (title, sub, src, r, actions = "") => () => head(title, sub, actions) + plain(src, r);

const TABS = {
  root: [
    ["Colleges", page("Colleges", "Register colleges and see how they use CampusLive.", "/api/colleges", "colleges", openBtn("college", "Create college"))],
    ["Activity logs", page("Activity logs", "Everything that happened across all colleges.", "/api/logs", "logs")], account],
  admin: [
    ["Live campus", () => head("Campus live", "Every lecture a teacher has made live, with student confirmation. Select a row for its full record.") + board()],
    ["Departments", page("Departments and HODs", "Create departments and manage their heads.", "/api/depts", "depts", openBtn("dept", "Add department"))],
    ["Teachers", page("Teachers", "Everyone teaching in the college and what they are doing now.", "/api/teachers", "teachers")],
    ["Schedule", page("Schedule", "Upcoming lectures across the college.", "/api/upcoming", "mine")],
    reports,
    ["History", page("Lecture history", "Every completed, cancelled and missed lecture.", "/api/history", "history")],
    ["Logs", page("Activity log", "A record of every action in your college.", "/api/logs", "logs")], account],
  hod: [
    ["Live department", () => head("Department live", "Lectures running in your department right now. Select a row for its full record.") + board()],
    ["Teachers", page("Teachers", "Teachers in your department.", "/api/teachers", "teachers", openBtn("teacher", "Add teacher"))],
    ["Classes", page("Classes", "Classes your department teaches.", "/api/classes", "classes", openBtn("class", "Add class"))],
    ["Substitutions", page("Substitutions and rooms", "Assign another teacher to a lecture that has not started, or move it to another room.", "/api/upcoming", "mine")],
    ["Timetables", page("Timetables", "Weekly slots set by your teachers.", "/api/timetable", "timetable")],
    reports,
    ["History", page("Lecture history", "Completed, cancelled and missed lectures in your department.", "/api/history", "history")],
    ["Logs", page("Activity log", "A record of every action in your department.", "/api/logs", "logs")], account],
  teacher: [
    ["My lectures", page("My lectures", "Make a lecture live from 10 minutes before it starts. Students confirm they are present with the class code on your live lecture. A lecture you forget to end finishes 15 minutes after its scheduled end.", "/api/upcoming", "mine", openBtn("lecture", "Schedule lecture"))],
    ["Weekly timetable", page("Weekly timetable", "Set a slot once and the lectures for the coming weeks are scheduled for you. Clashes are skipped.", "/api/timetable", "timetable", openBtn("slot", "Add weekly slot"))],
    ["Classes", page("Classes", "Classes you can schedule lectures for.", "/api/classes", "classes", openBtn("class", "Add class"))],
    ["History", page("My lecture history", "Your past lectures and how many students attended.", "/api/history", "history")], account],
  student: [
    ["Live now", () => head("Live now", "Lectures running for your class. Enter the class code your teacher shows to mark yourself present.") + board()],
    ["Schedule", page("Schedule", "Your class timetable.", "/api/upcoming", "mine")],
    ["History", page("Past lectures", "Your lectures and whether you were present.", "/api/history", "history")], account],
};
