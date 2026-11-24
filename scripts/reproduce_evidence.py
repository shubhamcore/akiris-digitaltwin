"""Rebuild synthetic data and record generation, schema and model evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], log: Path) -> tuple[str, float]:
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8",
                            errors="replace", stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - started
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Command failed with {result.returncode}. See {log}")
    return result.stdout, elapsed


def json_tail(output: str) -> dict:
    start = output.find("{")
    if start == -1:
        raise ValueError("No JSON object in command output")
    return json.loads(output[start:])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicles", type=int, default=2000,
                        help="Target finished vehicles, including scrapped vehicles")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mixed-runs", type=int, default=3)
    parser.add_argument("--full-runs", type=int, default=3)
    parser.add_argument("--output", default="docs/evidence/reproduction")
    args = parser.parse_args()
    destination = (ROOT / args.output).resolve()
    if destination.exists():
        raise SystemExit("Choose a new output directory to preserve prior evidence.")
    destination.mkdir(parents=True)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["TWIN_PROFILE_INGEST"] = "1"
    environment = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "seed": args.seed,
        "target_finished_vehicles": args.vehicles,
        "database": "SQLite, local filesystem",
        "execution": "Local Windows desktop with shared resources",
    }
    try:
        import psutil
        environment["physical_cpus"] = psutil.cpu_count(logical=False)
        environment["memory_bytes"] = psutil.virtual_memory().total
    except ImportError:
        pass
    (destination / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    run([sys.executable, "-m", "pip", "freeze"], destination / "requirements.freeze.txt")
    records = []
    scenarios = [("mixed", i+1) for i in range(args.mixed_runs)] + [("full", i+1) for i in range(args.full_runs)] + [("brownfield", 1)]
    for scenario, repetition in scenarios:
        name = f"{scenario}_{repetition}"
        database = destination / f"{name}.db"
        command = [sys.executable, "scripts/generate_data.py", "--scenario", scenario,
                   "--vehicles", str(args.vehicles), "--seed", str(args.seed),
                   "--db", str(database)]
        output, elapsed = run(command, destination / f"{name}_generation.log")
        summary = json_tail(output)
        record = {
            "scenario": scenario, "repetition": repetition, "command": command,
            "cli_wall_seconds": round(elapsed, 3), "summary": summary,
            "generated_events": sum(summary["event_counts"].values()),
        }
        with sqlite3.connect(database) as connection:
            names = [r[0] for r in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            record["tables"] = {n: connection.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0] for n in names}
            record["total_database_rows_after_generation"] = sum(record["tables"].values())
        if repetition == 1:
            os.environ["TWIN_MODEL_DIR"] = str(destination / f"{name}_models")
            trained, training_elapsed = run(
                [sys.executable, "scripts/train_models.py", "--db", str(database)],
                destination / f"{name}_training.log")
            record["training_wall_seconds"] = round(training_elapsed, 3)
            record["model_result"] = json_tail(trained)
            sys.path.insert(0, str(ROOT / "backend"))
            from sqlalchemy.orm import sessionmaker
            from app.db.session import make_engine
            from app.models import ProductionLine
            from app.services.data_quality import compute_station_data_quality
            engine = make_engine(f"sqlite:///{database.as_posix()}")
            with sessionmaker(bind=engine)() as session:
                line = session.query(ProductionLine).first()
                quality = compute_station_data_quality(session, line.id, persist=False)
                record["station_quality"] = quality
                record["mean_analytics_confidence"] = round(sum(r["analytics_confidence"] for r in quality)/len(quality),6)
                record["mean_sensor_coverage"] = round(sum(r["sensor_coverage"] for r in quality)/len(quality),6)
            engine.dispose()
        records.append(record)
        (destination / "results.json").write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
        print(name, "pipeline", summary["wall_seconds"], "s; CLI", round(elapsed,2),
              "s; events", record["generated_events"], "rows",
              record["total_database_rows_after_generation"], flush=True)
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
              for p in destination.iterdir() if p.is_file() and p.suffix in {".log",".json",".txt"}}
    (destination/"sha256.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
