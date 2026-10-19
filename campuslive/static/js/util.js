// Shared helpers: DOM, API calls, formatting, and small UI builders.
const $ = s => document.querySelector(s);
const e = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
let me = null, tab = 0, es = null, toastT;

async function api(u, body) {
  const r = await fetch(u, body === undefined ? {} : {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { const x = new Error(j.error || "Something went wrong"); x.status = r.status; throw x; }
  return j;
}
function toast(m) {
  const t = $("#toast"); t.textContent = m; t.style.display = "block";
  clearTimeout(toastT); toastT = setTimeout(() => t.style.display = "none", 4500);
}

const H12 = t => { if (!t) return "–"; const [h, m] = t.split(":").map(Number); return (h % 12 || 12) + ":" + String(m).padStart(2, "0") + " " + (h < 12 ? "AM" : "PM"); };
const T = s => s ? H12(s.slice(11, 16)) : "–";
const D = s => new Date(s + "T00:00").toLocaleDateString([], {weekday: "short", day: "numeric", month: "short"});
const today = () => { const d = new Date(); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
const initials = n => String(n || "?").split(/\s+/).map(x => x[0]).slice(0, 2).join("").toUpperCase();

const svg = d => `<svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
const ICON = {
  dots: `<svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor" aria-hidden="true"><circle cx="4" cy="10" r="1.7"/><circle cx="10" cy="10" r="1.7"/><circle cx="16" cy="10" r="1.7"/></svg>`,
  plus: svg('<path d="M10 4v12M4 10h12"/>'), x: svg('<path d="M5 5l10 10M15 5L5 15"/>'),
  out: svg('<path d="M8 4H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3M12 7l3 3-3 3M15 10H8"/>'),
};

const NAMES = {live: "Live", late: "Due, not started", available: "Ready to start", scheduled: "Scheduled", completed: "Completed", cancelled: "Cancelled", missed: "Not held"};
const tag = p => `<span class="tag ${p}">${NAMES[p] || p}</span>`;

// Tables. A blank heading marks the actions column (right aligned).
const tbl = (heads, rows, empty = "Nothing here yet.") => rows.length
  ? `<table><thead><tr>${heads.map(h => `<th${h === "" ? ' class="act"' : ""}>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map((c, i) => `<td${heads[i] === "" ? ' class="act"' : ""}>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`
  : `<div class="empty">${empty}</div>`;

// Page + card builders
const head = (title, sub = "", actions = "") => `<div class="pagehead"><div><h1>${title}</h1>${sub ? `<p class="sub">${sub}</p>` : ""}</div><div class="actions">${actions}</div></div>`;
const openBtn = (key, label, cls = "pri") => `<button class="btn ${cls}" data-open="${key}">${ICON.plus}${label}</button>`;
const box = (title, src, r) => `<section class="card"><div class="cardhead"><h2>${title}</h2></div><div class="scroll" data-src="${src}" data-r="${r}"></div></section>`;

// Forms (shown inside pop-up dialogs)
const fieldsHtml = f => f.map(([n, l, ty = "text", x = "", opt]) => ty === "hidden" ? `<input type="hidden" name="${n}" value="${x}">`
  : `<label>${l}<input name="${n}" type="${ty}" ${opt ? "" : "required"} ${x}></label>`).join("");
const foot = (btn, cls = "pri") => `<div class="mfoot"><button type="button" class="btn" data-close>Cancel</button><button class="btn ${cls}">${btn}</button></div>`;
const formHtml = (url, f, btn, ok = "Saved", cls = "pri") => `<form class="mform" data-post="${url}" data-ok="${ok}">${fieldsHtml(f)}${foot(btn, cls)}</form>`;
const confirmHtml = (text, url, btn, ok, f = []) => `<p class="mtext">${text}</p>` + formHtml(url, f, btn, ok, "danger");

// Three-dot menus
const menu = items => `<div class="kebab"><button class="dots" data-menu aria-label="More actions" aria-haspopup="true" aria-expanded="false">${ICON.dots}</button><div class="menu" role="menu" hidden>${items.join("")}</div></div>`;
const mi = (label, attrs, cls = "") => `<button class="mi ${cls}" role="menuitem" ${attrs}>${label}</button>`;
const rowact = (primary, items) => `<div class="rowact">${primary}${items.length ? menu(items) : ""}</div>`;
