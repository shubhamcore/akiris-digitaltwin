from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app.core.config import get_settings
from app.db.session import Base
from app.models import VehicleEvent, Inspection


def test_every_inspection_visit_has_one_matching_result(db):
    from collections import Counter
    expected = Counter(db.query(VehicleEvent.vehicle_id, VehicleEvent.station_id, VehicleEvent.inspection_result)
                       .filter(VehicleEvent.inspection_result.isnot(None)).all())
    actual = Counter(db.query(Inspection.vehicle_id, Inspection.station_id, Inspection.result).all())
    assert expected and actual == expected


def test_snapshot_invalidates_after_external_and_same_connection_writes(tmp_path):
    from sqlalchemy.orm import Session
    from app.services.read_snapshot import read_snapshot

    engine = create_engine(f"sqlite:///{tmp_path / 'snapshot.db'}")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql("CREATE TABLE sample (value INTEGER)")
        with Session(engine) as session:
            calls = []
            def compute():
                calls.append(1)
                return session.scalar(text("SELECT count(*) FROM sample"))

            assert read_snapshot(session, ("count",), compute) == 0
            assert read_snapshot(session, ("count",), compute) == 0
            assert len(calls) == 1
            with engine.begin() as other:
                other.exec_driver_sql("INSERT INTO sample VALUES (1)")
            assert read_snapshot(session, ("count",), compute) == 1
            session.execute(text("INSERT INTO sample VALUES (2)"))
            assert read_snapshot(session, ("count",), compute) == 2
            session.rollback()
            assert read_snapshot(session, ("count",), compute) == 1
    finally:
        engine.dispose()


def test_failed_stream_rolls_back_topology(tmp_path):
    import pytest
    from sqlalchemy.orm import sessionmaker
    from app.db.session import init_db
    from app.ingestion.pipeline import IngestionPipeline
    from app.ingestion.simulator_source import SimulatorDataSource
    from app.models import Plant

    class Interrupted(SimulatorDataSource):
        def stream(self, emit):
            raise ValueError("interrupted input")
    engine = init_db(f"sqlite:///{tmp_path / 'interrupted.db'}")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        with pytest.raises(ValueError, match="interrupted input"):
            IngestionPipeline(factory).ingest(Interrupted(get_settings().site_config))
        with factory() as session:
            assert session.query(Plant).count() == 0
    finally:
        engine.dispose()


def test_migration_roundtrip(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'migrations.db').as_posix()}"
    monkeypatch.setenv("TWIN_DATABASE_URL", url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    engine = create_engine(url)
    try:
        command.upgrade(config, "803153c85c70")
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO model_versions (name,algo,version,trained_at,metrics,artifact_path) "
                              "VALUES ('audit','rf','1',0,'{}','sample')"))
        for iteration in range(2):
            command.upgrade(config, "head")
            with engine.connect() as conn:
                inspector = inspect(conn)
                assert set(inspector.get_table_names()) - {"alembic_version"} == set(Base.metadata.tables)
                assert compare_metadata(MigrationContext.configure(conn), Base.metadata) == []
                assert conn.execute(text("PRAGMA foreign_key_check")).all() == []
                assert conn.scalar(text("SELECT status FROM model_versions WHERE name='audit'")) == "production"
                for table in Base.metadata.sorted_tables:
                    assert {x.name for x in table.indexes} == {x["name"] for x in inspector.get_indexes(table.name)}
                    assert [x.name for x in table.primary_key] == inspector.get_pk_constraint(table.name)["constrained_columns"]
            if iteration == 0:
                command.downgrade(config, "803153c85c70")
    finally:
        engine.dispose()
        get_settings.cache_clear()

