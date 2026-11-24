"""Inspect a migrated database. Accepts TWIN_DATABASE_URL via application settings."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.db.session import Base, engine
import app.models

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
configure_mappers()
with engine.connect() as connection:
    inspector = inspect(connection)
    tables = {}
    for name in sorted(set(inspector.get_table_names()) - {"alembic_version"}):
        tables[name] = {"primary_key": inspector.get_pk_constraint(name),
                        "foreign_keys": inspector.get_foreign_keys(name),
                        "indexes": inspector.get_indexes(name),
                        "unique": inspector.get_unique_constraints(name),
                        "checks": inspector.get_check_constraints(name)}
    differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    result = {"dialect": engine.dialect.name, "server_version": engine.dialect.server_version_info,
              "orm_table_count": len(Base.metadata.tables), "database_table_count": len(tables),
              "schema_differences": differences, "tables": tables}
    args.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    assert differences == [] and set(tables) == set(Base.metadata.tables), "Schema drift"

