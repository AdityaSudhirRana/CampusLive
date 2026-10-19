"""Server-Sent Events: pushes an update ping to dashboards of a college."""
import queue, threading
from flask import Blueprint, Response, jsonify
from .helpers import cur

bp = Blueprint("realtime", __name__)

# ---------- real-time (Server-Sent Events) ----------
subs, sub_lock = {}, threading.Lock()
def publish(college_id):
    with sub_lock:
        for key in (college_id, 0):
            for qu in subs.get(key, ()): qu.put(1)

@bp.get("/api/stream")
def stream():
    u = cur()
    if not u: return jsonify(error="Not signed in"), 401
    key = u["college_id"] or 0; qu = queue.Queue()
    with sub_lock: subs.setdefault(key, set()).add(qu)
    def gen():
        try:
            yield "retry: 2000\n\n"
            while True:
                try: qu.get(timeout=20); yield "data: update\n\n"
                except queue.Empty: yield ": ping\n\n"
        finally:
            with sub_lock: subs[key].discard(qu)
    return Response(gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

