"""Background job: auto-ends forgotten lectures, marks never-started ones as not held."""
import time, threading
from .db import q, ex
from .config import GRACE
from .helpers import now, mins, log
from .realtime import publish

# ---------- sweeper: auto-end forgotten lectures, mark never-held ones ----------
def sweep():
    while True:
        try:
            n = now(); today = n.strftime("%Y-%m-%d"); nm = n.hour * 60 + n.minute
            for l in q("SELECT * FROM lectures WHERE status IN ('LIVE','SCHEDULED')"):
                ids = (l["college_id"], l["dept_id"])
                over = l["date"] < today or (l["date"] == today and nm > mins(l["end_time"]) + (GRACE if l["status"] == "LIVE" else 0))
                if l["status"] == "LIVE" and over:
                    ex("UPDATE lectures SET status='COMPLETED', ended_at=? WHERE id=?", (l["date"] + "T" + l["end_time"] + ":00", l["id"]))
                    log(ids, None, "LECTURE_AUTO_ENDED", l["id"], f"{l['subject']}: teacher did not end it"); publish(l["college_id"])
                elif l["status"] == "SCHEDULED" and (l["date"] < today or (l["date"] == today and nm > mins(l["end_time"]))):
                    ex("UPDATE lectures SET status='MISSED' WHERE id=?", (l["id"],))
                    log(ids, None, "LECTURE_NOT_HELD", l["id"], f"{l['subject']} was never made live"); publish(l["college_id"])
        except Exception as e: print("sweep error", e)
        time.sleep(30)


def start():
    threading.Thread(target=sweep, daemon=True).start()
