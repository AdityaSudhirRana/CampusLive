// The live board: one row per lecture, laid out like a departures board.
R.board = d => {
  const student = me.role === "student";
  const num = (n, t, c = "") => `<div class="stat ${c}"><b>${n}</b><span>${t}</span></div>`;
  const plate = r => `<div class="plate"><small>Room</small>${e(r)}</div>`;
  const proof = l => student ? "" : `<span class="${l.verified ? "ok" : "pending"}">${l.verified ? "Verified by students" : "Awaiting student confirmation"}: ${l.present} of ${l.enrolled} present</span>`;
  const attr = l => student ? "" : `data-detail="${l.id}" tabindex="0"`;
  const live = l => `<div class="brow live" ${attr(l)}>${plate(l.room)}
    <div class="what"><b>${e(l.subject)}</b><span>${e(l.class_name)}</span>${proof(l)}${l.covering_for ? `<span>Covering for ${e(l.covering_for)}</span>` : ""}</div>
    <div class="who">${e(l.teacher)}</div>
    <div class="when"><b class="el" data-since="${e(l.started_at)}"></b><span>since ${T(l.started_at)}</span></div>${tag("live")}</div>`;
  const late = l => `<div class="brow late" ${attr(l)}>${plate(l.room)}
    <div class="what"><b>${e(l.subject)}</b><span>${e(l.class_name)}</span></div><div class="who">${e(l.teacher)}</div>
    <div class="when"><b>${H12(l.start_time)}</b><span>was due</span></div>${tag("late")}</div>`;
  const checkin = l => l.checked
    ? `<div class="checkin done">You are marked present in this lecture.</div>`
    : `<form class="checkin" data-post="/api/lectures/${l.id}/checkin" data-ok="You are marked present">
        <label>Class code from your teacher<input name="code" inputmode="numeric" maxlength="4" required></label>
        <button class="btn go">Mark me present</button></form>`;
  const sheet = (title, count, rows) => `<section class="card"><div class="cardhead"><h2>${title}</h2><span class="count">${count}</span></div>${rows}</section>`;

  if (student) {
    return sheet("Live for your class", d.live.length,
      d.live.length ? d.live.map(l => live(l) + checkin(l)).join("") : `<div class="empty">No lecture is live for your class right now.</div>`);
  }
  const by = {};
  d.live.forEach(l => (by[l.dept] ??= []).push(l));
  const stats = `<div class="stats">${num(d.live.length, "Live lectures", "l")}${num(d.live.filter(l => l.verified).length, "Verified by students", "v")}
    ${num(new Set(d.live.map(l => l.teacher)).size, "Active teachers")}${num(new Set(d.live.map(l => l.room)).size, "Occupied rooms")}${num(d.late.length, "Due but not started", "w")}</div>`;
  const groups = d.live.length
    ? Object.entries(by).map(([dep, ls]) => sheet(e(dep), ls.length + " live", ls.map(live).join(""))).join("")
    : `<section class="card"><div class="empty">No lectures are live at ${H12(d.now)}.</div></section>`;
  return stats + groups + (d.late.length ? sheet("Due but not started", d.late.length, d.late.map(late).join("")) : "");
};
