"""Start CampusLive:  python run.py        (add --demo to load sample data)"""
import os, socket, sys, threading, webbrowser

try:
    import flask  # noqa: F401
except ImportError:
    sys.exit("Flask is not installed. Run:  pip install -r requirements.txt")

from campuslive import create_app, config
from campuslive.sweeper import start


def is_free(host, port):
    with socket.socket() as probe:                       # something already listening?
        probe.settimeout(0.3)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            return False
    with socket.socket() as s:
        try:
            s.bind((host, port)); return True
        except OSError:
            return False


def pick_port(host, wanted):
    for port in range(wanted, wanted + 20):
        if is_free(host, port):
            return port
    sys.exit(f"No free port found from {wanted} to {wanted + 19}. Set PORT to another number.")


if __name__ == "__main__":
    app = create_app()
    if "--demo" in sys.argv or "--reset" in sys.argv:
        from campuslive.seed import seed
        force = "--reset" in sys.argv
        res = seed(force=force)
        print("Demo data loaded (Sheth L.U.J. & Sir M.V. College dataset)." if res else "Demo data already present.")
    host = os.environ.get("HOST", "127.0.0.1")
    port = pick_port(host, int(os.environ.get("PORT", 5000)))
    url = f"http://{'127.0.0.1' if host in ('0.0.0.0', '127.0.0.1') else host}:{port}"
    print(f"\n  CampusLive is running at {url}\n  Root login: {config.ROOT_USER} / {config.ROOT_PASSWORD}\n  Stop with Ctrl+C\n")
    start()
    if not os.environ.get("NO_BROWSER"):
        threading.Timer(1.2, webbrowser.open, [url]).start()
    app.run(host=host, port=port, threaded=True, use_reloader=False)
