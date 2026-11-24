"""Run the existing 60-user profile on a private copy of a synthetic SQLite snapshot."""
import argparse
import os
from contextlib import closing
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import signal
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("Supply an existing generated and trained SQLite database.")
    args.output.mkdir(parents=True, exist_ok=False)
    port = 18381
    host = f"http://127.0.0.1:{port}"
    with TemporaryDirectory() as tmp, (args.output / "api.log").open("w") as api_log:
        db = Path(tmp) / "load.db"
        with closing(sqlite3.connect(args.database)) as original, closing(sqlite3.connect(db)) as fresh:
            original.backup(fresh)
        env = dict(os.environ, TWIN_DATABASE_URL=f"sqlite:///{db.as_posix()}", PYTHONIOENCODING="utf-8")
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app",
            "--app-dir", "backend", "--host", "127.0.0.1", "--port", str(port),
            "--no-access-log"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            cwd=ROOT, env=env, stdout=api_log, stderr=subprocess.STDOUT)
        try:
            for _ in range(90):
                if server.poll() is not None:
                    raise RuntimeError("Server exited before readiness")
                try:
                    with urlopen(host + "/health", timeout=2) as r:
                        if r.status == 200:
                            break
                except OSError:
                    time.sleep(1)
            else:
                raise RuntimeError("Server did not become ready")
            command = [sys.executable, "-m", "locust", "-f", "load/locustfile.py",
                "--headless", "-u", "60", "-r", "15", "-t", "60s", "--host", host,
                "--csv", str((args.output / "locust").resolve()), "--only-summary"]
            with (args.output / "execution.log").open("w", encoding="utf-8") as out:
                subprocess.run(command, cwd=ROOT, env=env, stdout=out,
                               stderr=subprocess.STDOUT, check=True)
        finally:
            if os.name == "nt":
                server.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                server.terminate()
            server.wait(timeout=20)


if __name__ == "__main__":
    main()

