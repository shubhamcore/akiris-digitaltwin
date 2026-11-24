# Relational schema and migration verification

SQLAlchemy metadata, a freshly migrated SQLite database and PostgreSQL 16.16 each contained 22 application tables. Alembic adds one bookkeeping table. The initial revision creates 19 application tables; the next revision brings the migration history into alignment with the ORM. SQLite ran the populated-row upgrade/downgrade/re-upgrade regression. PostgreSQL ran empty-to-head, downgrade to revision 803153c85c70, re-upgrade, Alembic metadata comparison and a 60-finished-vehicle seed-7 simulation. These edges follow reflected foreign keys. Parent-side optionality is illustrative; inspect column nullability and constraints for exact semantics.

| Table | PK | Foreign keys | Indexes | Unique constraints | Check constraints |
|---|---|---|---|---|---|
| anomalies | id | 2 | 3 | 0 | 0 |
| data_quality_metrics | id | 1 | 1 | 0 | 0 |
| defects | id | 2 | 2 | 0 | 0 |
| environment_samples | id | 0 | 1 | 0 | 0 |
| inspections | id | 2 | 2 | 0 | 0 |
| machine_events | id | 1 | 1 | 0 | 0 |
| maintenance_queue | id | 2 | 2 | 0 | 0 |
| model_versions | id | 0 | 0 | 0 | 0 |
| plants | id | 0 | 0 | 1 | 0 |
| predictions | id | 2 | 2 | 0 | 0 |
| production_batches | id | 1 | 2 | 0 | 0 |
| production_lines | id | 1 | 1 | 0 | 0 |
| recommendations | id | 1 | 2 | 0 | 0 |
| sensor_readings | id | 2 | 3 | 0 | 0 |
| sensors | id | 1 | 1 | 0 | 0 |
| simulation_scenarios | id | 1 | 1 | 0 | 0 |
| station_kpis | id | 1 | 2 | 0 | 0 |
| station_types | id | 0 | 0 | 1 | 0 |
| stations | id | 2 | 4 | 0 | 0 |
| twin_context | id | 1 | 0 | 0 | 0 |
| vehicle_events | id | 2 | 2 | 0 | 0 |
| vehicles | id | 2 | 5 | 0 | 0 |

```mermaid
erDiagram
    anomalies {
        int id PK
    }
    stations |o--o{ anomalies : "station_id"
    vehicles |o--o{ anomalies : "vehicle_id"
    data_quality_metrics {
        int id PK
    }
    stations |o--o{ data_quality_metrics : "station_id"
    defects {
        int id PK
    }
    stations |o--o{ defects : "station_id"
    vehicles |o--o{ defects : "vehicle_id"
    environment_samples {
        int id PK
    }
    inspections {
        int id PK
    }
    stations |o--o{ inspections : "station_id"
    vehicles |o--o{ inspections : "vehicle_id"
    machine_events {
        int id PK
    }
    stations |o--o{ machine_events : "station_id"
    maintenance_queue {
        int id PK
    }
    production_lines |o--o{ maintenance_queue : "line_id"
    simulation_scenarios |o--o{ maintenance_queue : "scenario_id"
    model_versions {
        int id PK
    }
    plants {
        int id PK
    }
    predictions {
        int id PK
    }
    model_versions |o--o{ predictions : "model_version_id"
    vehicles |o--o{ predictions : "vehicle_id"
    production_batches {
        int id PK
    }
    production_lines |o--o{ production_batches : "line_id"
    production_lines {
        int id PK
    }
    plants |o--o{ production_lines : "plant_id"
    recommendations {
        int id PK
    }
    production_lines |o--o{ recommendations : "line_id"
    sensor_readings {
        int id PK
    }
    stations |o--o{ sensor_readings : "station_id"
    vehicles |o--o{ sensor_readings : "vehicle_id"
    sensors {
        int id PK
    }
    stations |o--o{ sensors : "station_id"
    simulation_scenarios {
        int id PK
    }
    production_lines |o--o{ simulation_scenarios : "line_id"
    station_kpis {
        int id PK
    }
    stations |o--o{ station_kpis : "station_id"
    station_types {
        int id PK
    }
    stations {
        int id PK
    }
    production_lines |o--o{ stations : "line_id"
    station_types |o--o{ stations : "type_id"
    twin_context {
        int id PK
    }
    production_lines |o--o{ twin_context : "active_line_id"
    vehicle_events {
        int id PK
    }
    stations |o--o{ vehicle_events : "station_id"
    vehicles |o--o{ vehicle_events : "vehicle_id"
    vehicles {
        int id PK
    }
    production_batches |o--o{ vehicles : "batch_id"
    production_lines |o--o{ vehicles : "line_id"
```

[SQLite reflection](evidence/sqlite-schema.json) · [PostgreSQL reflection](evidence/postgres-schema.json) · [PostgreSQL execution](evidence/postgres-final.log)

To repeat on Windows use an empty test directory and a local PostgreSQL bin directory. The script creates a password-protected loopback cluster, runs the checks and stops it. Point the ordinary Alembic commands only at the intended database. SQLAlchemy relationships are configured by the schema verifier. Alembic autogeneration and foreign-key checks complement tests but cannot prove every business invariant.
```powershell
./scripts/test_postgres.ps1 -Bin C:/PostgreSQL/bin -Scratch C:/Temp/twinline-new-cluster -Python (Get-Command python).Source
```
