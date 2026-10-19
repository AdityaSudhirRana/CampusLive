// Public pages: the home page and the sign-in / sign-up screens.
const mockRow = (room, subj, cls, who, mins, proof) => `<div class="brow live"><div class="plate"><small>Room</small>${room}</div>
  <div class="what"><b>${subj}</b><span>${cls}</span><span class="ok">${proof}</span></div><div class="who">${who}</div>
  <div class="when"><b>${mins}</b><span>so far</span></div><span class="tag live">Live</span></div>`;

function landingView() {
  const step = (n, t, p) => `<div class="step"><span class="num">${n}</span><h3>${t}</h3><p>${p}</p></div>`;
  const feat = (t, p) => `<div class="feat"><h3>${t}</h3><p>${p}</p></div>`;
  const role = (t, items) => `<div class="role"><h3>${t}</h3><ul>${items.map(i => `<li>${i}</li>`).join("")}</ul></div>`;
  $("#root").innerHTML = `<div class="land">
  <header class="lnav"><div class="brand"><span class="dot on"></span>CampusLive</div>
    <button class="l" data-scroll="how">How it works</button><button class="l" data-scroll="features">Features</button><button class="l" data-scroll="roles">Who it is for</button>
    <span class="sp"></span><a class="btn" href="#signup">Student sign up</a><a class="btn pri" href="#signin">Sign in</a></header>
  <section class="hero"><div class="copy"><span class="pill"><i class="dot on"></i>Live lecture monitoring for colleges</span>
    <h1>Know which lectures are actually happening, right now.</h1>
    <p>A timetable shows the plan. CampusLive shows what is really going on: the teacher makes a lecture live, students confirm it, and the principal and HODs see it as it happens.</p>
    <div class="ctas"><a class="btn pri lg" href="#signin">Sign in to CampusLive</a><a class="btn lg" href="#signup">Student sign up</a></div>
    <p class="small">Made for principals, heads of department, teachers and students.</p></div>
    <div class="mock card"><div class="cardhead"><h2>Campus live</h2><span class="count">4 lectures live</span></div>
      ${mockRow("204", "Data Structures", "FY B.Sc. CS", "Prof. Mehta", "38 min", "Verified by students: 31 of 40 present")}
      ${mockRow("102", "Accounts", "SY B.Com", "Prof. Desai", "22 min", "Verified by students: 24 of 36 present")}
      ${mockRow("Lab 2", "Physics Practical", "FY B.Sc.", "Dr. Verma", "9 min", "Awaiting student confirmation: 1 of 28 present")}</div></section>
  <section class="band" id="how"><h2>From the timetable to a verified live lecture</h2><div class="steps">
    ${step(1, "The teacher makes it live", "At the scheduled time the teacher taps Make live. The lecture becomes official and appears on every dashboard.")}
    ${step(2, "Students confirm it", "A 4-digit class code is shown only to the teacher. Students enter it, and the lecture shows as verified.")}
    ${step(3, "Leaders see it instantly", "Principals and HODs watch lectures by department, room and teacher, with no refreshing and no phone calls.")}</div></section>
  <section class="band alt" id="features"><h2>Everything a college needs to run lectures in one place</h2><div class="fgrid">
    ${feat("Live campus board", "See every running lecture, who is teaching, where, and for how long.")}
    ${feat("Student verification", "Check-ins with a class code show which live lectures are really being held.")}
    ${feat("Weekly timetables", "Create a slot once and the next weeks of lectures are scheduled, with clash checks.")}
    ${feat("Substitutions and rooms", "HODs can assign a substitute or change a room, and everyone sees it at once.")}
    ${feat("Reports", "Held rate, average start delay and attendance per teacher, with CSV export.")}
    ${feat("Complete activity log", "Every start, end, change and cancellation is recorded for review.")}</div></section>
  <section class="band" id="roles"><h2>One platform for everyone in the chain</h2><div class="rgrid">
    ${role("Principal", ["Live view of the whole college", "Drill into any lecture", "Manage HODs", "College-wide reports"])}
    ${role("Head of department", ["Live view of the department", "Add teachers and classes", "Substitutions and room changes", "Department reports"])}
    ${role("Teacher", ["Weekly timetable", "Make lectures live and end them", "Class code for check-in", "Own history"])}
    ${role("Student", ["See what is live for your class", "Mark yourself present", "Your schedule", "Your attendance history"])}</div></section>
  <section class="cta"><h2>Ready to see your college live?</h2><a class="btn pri lg" href="#signin">Sign in</a></section>
  <footer class="lfoot"><div class="brand"><span class="dot on"></span>CampusLive</div><span>Real-time academic activity monitoring for colleges.</span></footer></div>`;
}

function authView(register) {
  const signIn = `<h2>Welcome back</h2><p class="mut">Sign in to your CampusLive account.</p>
    <form class="mform one" data-post="/api/login">${fieldsHtml([["username", "Username", "text", 'autocomplete="username"'], ["password", "Password", "password", 'autocomplete="current-password"']])}
    <div class="mfoot"><button class="btn pri lg block">Sign in</button></div></form>
    <p class="alt">New student? <a href="#signup">Create your account</a></p>`;
  const signUp = `<h2>Student sign up</h2><p class="mut">Use the college code your college gave you.</p>
    <form class="mform one" data-post="/api/register">
      <label>College code<input name="college_code" id="cc" placeholder="COL001" required></label>
      <label>Your class<select name="class_id" id="cls" required><option value="">Enter the college code first</option></select></label>
      ${fieldsHtml([["name", "Your name"], ["username", "Username"], ["password", "Password", "password", 'minlength="6"']])}
      <div class="mfoot"><button class="btn pri lg block">Create account</button></div></form>
    <p class="alt">Already have an account? <a href="#signin">Sign in</a></p>`;
  $("#root").innerHTML = `<div class="gate"><section class="pitch"><a class="brand" href="#"><span class="dot on"></span>CampusLive</a>
    <h2>What is being taught right now?</h2><p>Teachers make lectures live. Principals, HODs and students see them as they happen.</p></section>
    <section class="access"><a class="back" href="#">Back to home</a>${register ? signUp : signIn}</section></div>`;
}
