// Renderers: each takes the JSON from an API endpoint and returns HTML.
const cov = l => l.covering_for ? `<div class="mut">Covering for ${e(l.covering_for)}</div>` : "";
const sub2 = (a, b) => `<b>${a}</b><div class="mut">${b}</div>`;
const staff = () => me.role !== "student";
const liveInfo = l => l.phase === "live" && staff() ? `<div class="mut">${l.present} of ${l.enrolled} present${l.code ? `. Class code <b class="code">${e(l.code)}</b>` : ""}</div>` : "";
const active = on => on ? '<span class="tag ok">Active</span>' : '<span class="tag cancelled">Deactivated</span>';
const acctMenu = (id, on) => menu([mi("Reset password", `data-open="pw" data-id="${id}"`),
  on ? mi("Deactivate account", `data-open="deactivate" data-id="${id}"`, "danger") : mi("Reactivate account", `data-act="active" data-id="${id}" data-on="1"`)]);

const startable = l => ["available", "late"].includes(l.phase), pending = l => ["scheduled", "available", "late"].includes(l.phase);
const teacherRow = l => rowact(
  startable(l) ? `<button class="btn go sm" data-act="start" data-id="${l.id}">Make live</button>`
    : l.phase === "live" ? `<button class="btn sm" data-act="end" data-id="${l.id}">End lecture</button>`
    : l.phase === "scheduled" ? `<button class="btn sm" disabled title="Opens 10 minutes before the start time">Make live</button>` : "",
  [...(pending(l) || l.phase === "live" ? [mi("Change room", `data-open="room" data-id="${l.id}"`)] : []),
   ...(pending(l) ? [mi("Cancel lecture", `data-open="cancel" data-id="${l.id}"`, "danger")] : [])]);
const hodRow = l => rowact("", [...(pending(l) ? [mi("Substitute teacher", `data-open="sub" data-id="${l.id}"`)] : []),
  ...(pending(l) || l.phase === "live" ? [mi("Change room", `data-open="room" data-id="${l.id}"`)] : [])]);

const R = {
  colleges: d => tbl(["College", "Principal", "Departments", "Teachers", "Live now", "Lectures logged"],
    d.map(c => [sub2(e(c.name), c.code), e(c.admin), c.depts, c.teachers, c.live ? tag("live") + " " + c.live : "0", c.total]), "No colleges yet. Create the first one."),
  depts: d => tbl(["Department", "Head of department", "Teachers", "Live now", "Status", ""],
    d.map(x => [`<b>${e(x.name)}</b>`, sub2(e(x.hod), e(x.hod_login)), x.teachers, x.live, active(x.hod_active), acctMenu(x.hod_id, x.hod_active)]), "No departments yet."),
  teachers: d => tbl(["Teacher", "Contact", "Department", "Right now", "Status", ""],
    d.map(t => [sub2(e(t.name), e(t.username)), t.email || t.phone ? `${e(t.email || "")}<div class="mut">${e(t.phone || "")}</div>` : '<span class="mut">Not added</span>', e(t.dept),
      t.live_now ? tag("live") + `<div class="mut">${e(t.live_now)}</div>` : '<span class="mut">Not teaching</span>', active(t.active), acctMenu(t.id, t.active)]), "No teachers yet."),
  classes: d => tbl(["Classes in your department"], d.map(c => [e(c.name)]), "No classes yet."),
  classOpts: d => d.length ? d.map(c => `<option value="${c.id}">${e(c.name)}</option>`).join("") : `<option value="">Add a class first</option>`,
  logs: d => tbl(["Time", "College", "Event", "By", "Details"],
    d.map(l => [`${D(l.ts.slice(0, 10))}<div class="mut">${T(l.ts)}</div>`, e(l.college), `<b>${e(l.event.replaceAll("_", " "))}</b>`, e(l.actor), e(l.detail)]), "No activity recorded yet."),
  history: d => me.role === "student"
    ? tbl(["Date", "Lecture", "Teacher and room", "Time", "Your attendance", "Status"],
        d.map(l => [D(l.date), sub2(e(l.subject), e(l.class_name)), e(l.teacher) + `<div class="mut">Room ${e(l.room)}</div>`, H12(l.start_time) + " – " + H12(l.end_time),
          l.status === "COMPLETED" ? (l.checked ? '<span class="tag ok">Present</span>' : '<span class="tag cancelled">Absent</span>') : '<span class="mut">–</span>', tag(l.status.toLowerCase())]), "Completed lectures will appear here.")
    : tbl(["Date", "Lecture", "Teacher and room", "Scheduled and actual", "Present", "Status", ""],
        d.map(l => [D(l.date), sub2(e(l.subject), e(l.class_name)) + cov(l), e(l.teacher) + `<div class="mut">Room ${e(l.room)}</div>`,
          H12(l.start_time) + " – " + H12(l.end_time) + (l.started_at ? `<div class="mut">Live ${T(l.started_at)} to ${T(l.ended_at)}</div>` : ""),
          `${l.present} of ${l.enrolled}`, tag(l.status.toLowerCase()), `<button class="btn sm" data-detail="${l.id}">View</button>`]), "Completed lectures will appear here."),
  mine: d => {
    const t = me.role === "teacher", h = me.role === "hod", ops = t || h;
    return tbl(["Date", "Time", "Lecture", t ? "Room" : "Teacher and room", "Status", ...(ops ? [""] : [])],
      d.map(l => [D(l.date), H12(l.start_time) + " – " + H12(l.end_time), sub2(e(l.subject), e(l.class_name)) + cov(l),
        t ? e(l.room) : e(l.teacher) + `<div class="mut">Room ${e(l.room)}</div>`, tag(l.phase) + liveInfo(l), ...(ops ? [t ? teacherRow(l) : hodRow(l)] : [])]), "No upcoming lectures.");
  },
  timetable: d => {
    const h = me.role === "hod", t = me.role === "teacher";
    return tbl(["Day", "Time", "Lecture", "Room", ...(h ? ["Teacher"] : []), ...(t ? [""] : [])],
      d.map(s => [s.day, H12(s.start_time) + " – " + H12(s.end_time), sub2(e(s.subject), e(s.class_name)), e(s.room), ...(h ? [e(s.teacher)] : []),
        ...(t ? [rowact("", [mi("Remove weekly slot", `data-open="ttdel" data-id="${s.id}"`, "danger")])] : [])]), "No weekly slots yet.");
  },
  report: d => tbl(["Teacher", "Scheduled", "Held", "Not held", "Cancelled", "Held rate", "Avg start delay", "Avg attendance"],
    d.map(r => [sub2(e(r.teacher), e(r.dept)), r.total, r.held, r.missed, r.cancelled, r.rate == null ? "–" : r.rate + "%",
      r.delay == null ? "–" : (r.delay > 0 ? "+" : "") + r.delay + " min", r.attendance == null ? "–" : r.attendance + "%"]), "No lecture activity in this period yet."),
  detail: d => {
    const l = d.lecture, fact = (b, s) => `<div><b>${b}</b><span>${s}</span></div>`;
    return `<p class="mtext">${tag(l.phase)} ${e(l.class_name)}, ${e(l.dept)}, room ${e(l.room)}. Taught by ${e(l.teacher)}.${l.covering_for ? ` Covering for ${e(l.covering_for)}.` : ""}</p>
      <div class="facts">${fact(H12(l.start_time), "Scheduled start")}${fact(T(l.started_at), "Went live")}${fact(T(l.ended_at), "Ended")}${fact(l.present + " of " + l.enrolled, "Students present")}</div>
      <h3>Verification</h3><p class="mtext">${l.verified ? "Students in the class confirmed with the class code that this lecture is being held." : "No student confirmation yet. Only the teacher's own action marks this lecture live."}</p>
      <h3>Timeline</h3>${tbl(["Time", "Event", "By"], d.events.map(x => [T(x.ts), e(x.event.replaceAll("_", " ")) + (x.detail ? `<div class="mut">${e(x.detail)}</div>` : ""), e(x.actor)]), "No events recorded.")}
      ${d.present.length ? `<h3>Present</h3><p class="mtext">${d.present.map(p => e(p.name)).join(", ")}</p>` : ""}`;
  },
  profile: d => {
    const u = d.user, row = (l, v) => `<div><span>${l}</span><b>${v ? e(v) : '<i class="mut">Not added</i>'}</b></div>`;
    return `<section class="card"><div class="profile"><span class="avatar xl">${initials(u.name)}</span>
        <div class="grow"><h2>${e(u.name)}</h2><p class="mut">${ROLES[u.role]}${u.college ? ", " + e(u.college.name) : ""}${u.dept ? ", " + e(u.dept) : ""}</p></div>
        <button class="btn" data-open="profile">Edit profile</button></div>
      <div class="detailgrid">${row("Username", u.username)}${row("Email", u.email)}${row("Phone", u.phone)}${row("Role", ROLES[u.role])}</div></section>
      <section class="card"><div class="cardhead"><div><h2>Password</h2><p class="mut tight">Use at least 6 characters.</p></div><button class="btn" data-open="password">Change password</button></div></section>`;
  },
};
