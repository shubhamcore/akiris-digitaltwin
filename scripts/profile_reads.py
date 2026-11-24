"""Count SQL calls and time real responses for the dashboard read paths."""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("database", type=Path)
p.add_argument("output", type=Path)
args = p.parse_args()
assert args.database.is_file()
os.environ["TWIN_DATABASE_URL"] = f"sqlite:///{args.database.resolve().as_posix()}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import event
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine

results = {}
statements = []
@event.listens_for(engine, "before_cursor_execute")
def count(conn, cursor, statement, params, context, executemany):
    statements.append(statement)

with TestClient(app) as client:
    for path in ["/vehicles?limit=200", "/stations", "/bottlenecks", "/production/summary",
                 "/production/trends?bucket_vehicles=50", "/defect-risks?threshold=0.4&limit=40",
                 "/vehicles/2520/journey", "/health"]:
        statements.clear()
        start = time.perf_counter()
        response = client.get(path)
        response.raise_for_status()
        payload = json.dumps(response.json(), sort_keys=True).encode()
        results[path] = {"seconds": round(time.perf_counter()-start, 4), "queries": len(statements),
                         "body_sha256": hashlib.sha256(payload).hexdigest(),
                         "distinct_sql": list(dict.fromkeys(statements))}
args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")

