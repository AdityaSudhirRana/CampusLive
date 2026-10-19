// App shell: routing, navigation, dialogs, menus, live refresh.
function tickEl() {
  document.querySelectorAll(".el").forEach(x => {
    const m = Math.max(0, Math.floor((Date.now() - new Date(x.dataset.since)) / 60000));
    x.textContent = m < 60 ? m + " min" : Math.floor(m / 60) + " h " + (m % 60) + " min";
  });
}

async function hydrate() {
  if (me?.role === "hod") STAFF = await api("/api/teachers").catch(() => STAFF);
  for (const el of document.querySelectorAll("[data-src]")) {
    if (el.innerHTML !== "" && el.contains(document.activeElement) && document.activeElement.matches("input,select")) continue;   // don't wipe what someone is typing
    try {
      const data = await api(el.dataset.src), keep = el.value;
      el.innerHTML = R[el.dataset.r](data);
      if (el.tagName === "SELECT") el.value = keep || el.options[0]?.value;
    } catch (x) {
      if (x.status === 401) return boot();
      el.innerHTML = `<div class="empty">${e(x.message)}</div>`;
    }
  }
  tickEl();
}

function shell() {
  const tabs = TABS[me.role];
  const org = me.college ? `<b>${e(me.college.name)}</b>${e(me.dept || me.college.code)}` : "<b>CampusLive</b>Platform administration";
  $("#root").innerHTML = `<div class="app"><aside class="rail">
    <div class="brand"><span class="dot on"></span>CampusLive</div><div class="org">${org}</div>
    <nav>${tabs.map((x, i) => `<button class="${i === tab ? "on" : ""}" data-tab="${i}">${x[0]}</button>`).join("")}</nav>
    <div class="chip"><span class="avatar">${initials(me.name)}</span>
      <button class="who" data-goto="Account" title="Your account"><b>${e(me.name)}</b><span>${ROLES[me.role]}</span></button>
      <button class="out" data-act="logout" title="Sign out" aria-label="Sign out">${ICON.out}</button></div>
  </aside><div class="workspace"><div class="topbar"><span class="conn" id="conn"><i class="dot"></i>Connecting</span><span class="clock" id="clk"></span></div>
  <main>${tabs[tab][1]()}</main></div></div>`;
  hydrate();
}

function connect() {
  es?.close(); es = new EventSource("/api/stream");
  const set = (on, t) => { const c = $("#conn"); if (c) { c.classList.toggle("on", on); c.lastChild.textContent = t; } };
  es.onopen = () => set(true, "Live updates connected");
  es.onerror = () => set(false, "Reconnecting");
  es.onmessage = () => hydrate();
}

function route() {
  if (me) return;
  const h = location.hash;
  h === "#signin" ? authView(false) : h === "#signup" ? authView(true) : landingView();
  scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

async function boot() {
  try { me = (await api("/api/me")).user; } catch { me = null; }
  if (!me) { es?.close(); closeModal(); return route(); }
  history.replaceState(null, "", location.pathname); tab = 0; shell(); connect();
}

// ----- dialogs -----
function showModal(title, html, wide) {
  closeModal();
  document.body.insertAdjacentHTML("beforeend", `<div class="modal" id="modal" data-backdrop><div class="dialog ${wide ? "wide" : ""}" role="dialog" aria-modal="true" aria-label="${e(title)}">
    <div class="dhead"><h2>${e(title)}</h2><button class="x" data-close aria-label="Close">${ICON.x}</button></div><div class="dbody">${html}</div></div></div>`);
  $("#modal input:not([type=hidden]),#modal select")?.focus();
  hydrate();
}
const closeModal = () => $("#modal")?.remove();

async function openDetail(id) {
  try { const d = await api(`/api/lectures/${id}/detail`); showModal(d.lecture.subject, R.detail(d), true); }
  catch (x) { toast(x.message); }
}

// ----- three-dot menus -----
function closeMenus() {
  document.querySelectorAll(".menu:not([hidden])").forEach(m => { m.hidden = true; m.previousElementSibling?.setAttribute("aria-expanded", "false"); });
}
function toggleMenu(btn) {
  const m = btn.nextElementSibling, wasOpen = !m.hidden;
  closeMenus(); if (wasOpen) return;
  m.hidden = false; btn.setAttribute("aria-expanded", "true");
  const r = btn.getBoundingClientRect(), w = m.offsetWidth, h = m.offsetHeight;
  m.style.left = Math.max(8, Math.min(innerWidth - w - 8, r.right - w)) + "px";
  m.style.top = (r.bottom + 6 + h > innerHeight ? Math.max(8, r.top - h - 6) : r.bottom + 6) + "px";
}

// ----- events -----
document.addEventListener("submit", async ev => {
  const f = ev.target.closest("[data-post]"); if (!f) return;
  ev.preventDefault();
  const btn = f.querySelector("button:not([type=button])"); if (btn) btn.disabled = true;
  try {
    const r = await api(f.dataset.post, Object.fromEntries(new FormData(f)));
    if (["/api/login", "/api/register"].includes(f.dataset.post)) return boot();
    if (f.dataset.post === "/api/me/profile") { me = r.user; closeModal(); toast("Profile updated"); return shell(); }
    toast(r.code ? `College created. Its ID is ${r.code}`
      : r.made !== undefined ? `Weekly slot saved: ${r.made} lectures scheduled` + (r.skipped ? `, ${r.skipped} skipped for clashes. ${r.reasons[0]}` : "")
      : f.dataset.ok || "Saved");
    closeModal(); f.reset(); hydrate();
  } catch (x) { toast(x.message); if (btn) btn.disabled = false; }
});

document.addEventListener("click", async ev => {
  const t = ev.target;
  const dots = t.closest("[data-menu]"); if (dots) return toggleMenu(dots);
  closeMenus();
  if (t.dataset.backdrop !== undefined || t.closest("[data-close]")) return closeModal();
  const det = t.closest("[data-detail]");
  if (det && (det.tagName === "BUTTON" || !t.closest("button,a,input,select,form"))) return openDetail(det.dataset.detail);
  const op = t.closest("[data-open]");
  if (op) { const m = MODALS[op.dataset.open](op.dataset.id); return showModal(m.title, m.html, m.wide); }
  const sc = t.closest("[data-scroll]"); if (sc) return document.getElementById(sc.dataset.scroll)?.scrollIntoView({behavior: "smooth"});
  const go = t.closest("[data-goto]"); if (go) { tab = TABS[me.role].findIndex(x => x[0] === go.dataset.goto); return shell(); }
  const nav = t.closest("[data-tab]"); if (nav) { tab = +nav.dataset.tab; return shell(); }
  const a = t.closest("[data-act]"); if (!a) return;
  const act = a.dataset.act, id = a.dataset.id;
  if (act === "logout") { await api("/api/logout", {}); me = null; location.hash = ""; return boot(); }
  if (act === "days") { repDays = +a.dataset.d; return shell(); }
  try {
    if (act === "start" || act === "end") { await api(`/api/lectures/${id}/${act}`, {}); toast(act === "start" ? "Lecture is now live" : "Lecture completed"); }
    else if (act === "active") { await api(`/api/users/${id}/active`, {active: +a.dataset.on}); toast("Account reactivated"); }
    hydrate();
  } catch (x) { toast(x.message); }
});

document.addEventListener("change", async ev => {
  if (ev.target.id !== "cc") return;
  const r = await api("/api/public/classes?code=" + encodeURIComponent(ev.target.value)).catch(() => ({}));
  $("#cls").innerHTML = r.college
    ? `<option value="">Choose your class</option>` + r.classes.map(c => `<option value="${c.id}">${e(c.dept)}: ${e(c.name)}</option>`).join("")
    : `<option value="">College not found</option>`;
});
document.addEventListener("keydown", ev => { if (ev.key === "Escape") { closeMenus(); closeModal(); } });
window.addEventListener("scroll", closeMenus, true);
window.addEventListener("resize", closeMenus);

setInterval(() => { const c = $("#clk"); if (c) c.textContent = new Date().toLocaleDateString([], {weekday: "long", day: "numeric", month: "long"}) + ", " + new Date().toLocaleTimeString([], {hour: "numeric", minute: "2-digit"}); tickEl(); }, 1000);
setInterval(() => { if (me && !$("#modal") && !document.activeElement?.matches("input,select")) hydrate(); }, 30000);
boot();
