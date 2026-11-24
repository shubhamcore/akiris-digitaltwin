#!/usr/bin/env python3
"""Build the digital-twin database from a DataSource (simulator by default).

Examples:
  python scripts/generate_data.py --fresh --scenario mixed --vehicles 2000 --seed 42
  python scripts/generate_data.py --fresh --scenario brownfield --vehicles 2000 \
      --db data/generated/twinline_brownfield.db
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import init_db  # noqa: E402
from app.ingestion.pipeline import IngestionPipeline  # noqa: E402
from app.ingestion.simulator_source import SimulatorDataSource  # noqa: E402


def resolve_url(arg: str | None, default: str) -> str:
    if not arg:
        return default
    return arg if "://" in arg else f"sqlite:///{arg}"


def main() -> None:
    s = get_settings()
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="mixed", choices=["full", "mixed", "brownfield"])
    ap.add_argument("--vehicles", type=int, default=s.default_vehicles)
    ap.add_argument("--seed", type=int, default=s.default_seed)
    ap.add_argument("--db", default=None, help="sqlite path or full SQLAlchemy URL")
    ap.add_argument("--fresh", action="store_true", help="delete the target sqlite file first")
    args = ap.parse_args()

    url = resolve_url(args.db, s.database_url)
    if args.fresh and url.startswith("sqlite:///"):
        Path(url.split("///", 1)[1]).unlink(missing_ok=True)

    engine = init_db(url)
    sf = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    src = SimulatorDataSource(s.site_config, scenario=args.scenario,
                              seed=args.seed, vehicles=args.vehicles,
                              max_seconds=s.max_sim_seconds)
    print(f"ingesting: scenario={args.scenario} vehicles={args.vehicles} seed={args.seed}")
    from sqlalchemy.engine import make_url
    print(f"database : {make_url(url).render_as_string(hide_password=True)}")
    import os
    import time
    from sqlalchemy import event
    sql_write = 0.0
    if os.environ.get("TWIN_PROFILE_INGEST") == "1":
        @event.listens_for(engine, "before_cursor_execute")
        def before(conn, cursor, statement, parameters, context, executemany):
            context.write_start = (time.perf_counter() if statement.lstrip().upper().startswith(
                ("INSERT ", "UPDATE ", "DELETE ")) else None)

        @event.listens_for(engine, "after_cursor_execute")
        def after(conn, cursor, statement, parameters, context, executemany):
            nonlocal sql_write
            if context.write_start is not None:
                sql_write += time.perf_counter() - context.write_start
    summary = IngestionPipeline(sf).ingest(src)
    if "stage_seconds" in summary:
        summary["stage_seconds"]["sql_write_cursor_nested"] = round(sql_write, 4)
        summary["stage_seconds"]["pipeline_outside_stream"] = round(
            summary["wall_seconds"] - summary["stage_seconds"]["stream_inclusive"], 4)

    keep = {k: summary[k] for k in ("scenario", "spawned", "completed", "scrapped",
                                    "sim_seconds", "bad_batches", "ingest_stats",
                                    "wall_seconds", "event_counts", "stage_seconds") if k in summary}
    keep["top_utilization"] = dict(list(summary["utilization"].items())[:5])
    print(json.dumps(keep, indent=2))


if __name__ == "__main__":
    main()
