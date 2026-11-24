# TwinLine architecture

```mermaid
flowchart LR
  config[Site and scenario YAML] --> sim[42-station SimPy assembly line]
  sim --> etl[Event callbacks and cycle aggregation]
  replay[CSV or JSONL replay adapter] --> etl
  etl --> db[(SQLite or PostgreSQL)]
  db --> analytics[Genealogy, bottleneck and station observability]
  db --> models[Offline Random Forest and Isolation Forest]
  models --> db
  analytics --> api[FastAPI service]
  api --> ui[React supervisor, manager and leadership views]
  api --> prom[Prometheus metrics]
  prom --> graf[Optional Grafana]
```

## Ingestion and data flow

```mermaid
flowchart TD
  topology[Provision configured line, stations and sensors] --> stream[Consume normalized events]
  stream --> visit[Pair vehicle entry and exit at each station]
  stream --> samples[Accumulate samples within a visit]
  samples --> agg[Calculate count, mean, deviation and range]
  visit --> disposition[Resolve inspection on next visit, defect or finish]
  agg --> bulk[Bulk-insert visit, reading and inspection buffers]
  disposition --> bulk
  stream --> kpi[Buffer KPI, environment and machine events]
  kpi --> bulk
  bulk --> commit[Commit completed ingestion transaction]
  commit --> train[Offline features and advisory analytics]
```

Station topology and the synthetic event stream come from site YAML and scenario overrides. The pipeline records observations, preserves genealogy and commits the run. End-of-paint defect-risk features use historical measurements. A separate Isolation Forest identifies unusual instrumented visits. The browser communicates with FastAPI through the Vite development proxy. The PostgreSQL and SQLite backends share the same ORM. Dashboard snapshots on SQLite invalidate on database changes. The [ER diagram](database_schema.md) covers the physical schema.
