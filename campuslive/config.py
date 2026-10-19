"""Settings. Override with environment variables."""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.environ.get("CAMPUSLIVE_DB", os.path.join(BASE, "campuslive.db"))
SECRET_KEY = os.environ.get("SECRET_KEY", "campuslive-dev-secret-change-me")
ROOT_USER = os.environ.get("ROOT_USER", "root")
ROOT_PASSWORD = os.environ.get("ROOT_PASSWORD", "root123")
EARLY = 10   # minutes before the scheduled start that a teacher may go live
VERIFY_MIN = 2  # students who must check in before a lecture shows as verified
GRACE = 15   # minutes after the scheduled end before a forgotten live lecture is auto-ended
