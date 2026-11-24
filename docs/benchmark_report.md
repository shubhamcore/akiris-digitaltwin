# Simulation and ingestion benchmark

Seed 42, one Python process, local SQLite on D:, Windows 11, Intel Core i5-1335U (10 cores / 12 logical processors), 16,876,888,064 bytes of RAM, Python 3.12.14. Other desktop and audit processes shared the machine. Each database began empty. The stop condition is 2,000 terminal vehicles. The full run spawned 2,696 vehicles, accepted 1,888, scrapped 112 and left 696 in progress. The simulation clock advanced 121,401.9 virtual seconds.

| Scenario / run | Events | Rows | Accepted | Scrapped | Pipeline s | CLI wall s |
|---|---|---|---|---|---|---|
| mixed 1 | 837,428 | 384,707 | 1897 | 103 | 33.6795 | 36.428 |
| full 1 | 1,389,326 | 568,883 | 1888 | 112 | 40.9632 | 42.849 |
| full 2 | 1,389,326 | 568,883 | 1888 | 112 | 51.771 | 53.897 |
| full 3 | 1,389,326 | 568,883 | 1888 | 112 | 41.3933 | 43.673 |
| brownfield 1 | 379,425 | 226,940 | 1865 | 135 | 16.3664 | 19.531 |

Three instrumented full runs produced identical counts. Pipeline minimum / median / maximum were 40.96 / 41.39 / 51.77 seconds. CLI wall minimum / median / maximum were 42.85 / 43.67 / 53.90 seconds. A fourth full run with stage profiling disabled took **38.34 pipeline seconds** and **41.15 CLI seconds**. Stage instrumentation adds callback overhead. No cross-version speedup estimate follows from these runs.

| Clock (seconds) | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| stream_inclusive | 40.0882 | 50.9715 | 40.4692 |
| simulation_outside_emit | 10.5219 | 13.5573 | 10.4767 |
| event_dispatch_excluding_etl | 3.6696 | 4.4625 | 3.6923 |
| etl_handler_including_sql | 25.8967 | 32.9518 | 26.3002 |
| sql_write_cursor_nested | 3.709 | 4.5154 | 3.8147 |
| pipeline_outside_stream | 0.875 | 0.7995 | 0.9241 |

The simulation driver runs synchronously. The three exclusive in-stream clocks cover simulator work outside emit, event dispatch outside the handler, and the ingestion handler including its SQL. Time outside the stream includes topology, final buffers and transaction commit. SQL cursor write time overlaps ETL and includes driver execution of INSERT/UPDATE/DELETE. Commit, ORM preparation, reads and filesystem writeback cannot be assigned to this nested counter. Event construction inside the simulation engine before the callback stays in the simulator clock. CLI includes process imports and schema initialization. Training, dashboard startup and Locust are separate workloads.

## Database reconciliation

| Table | Full | Mixed | Brownfield |
|---|---|---|---|
| anomalies | 0 | 0 | 0 |
| data_quality_metrics | 0 | 0 | 0 |
| defects | 112 | 103 | 135 |
| environment_samples | 2023 | 2034 | 2026 |
| inspections | 12297 | 12355 | 12214 |
| machine_events | 122 | 128 | 128 |
| maintenance_queue | 0 | 0 | 0 |
| model_versions | 0 | 0 | 0 |
| plants | 1 | 1 | 1 |
| predictions | 0 | 0 | 0 |
| production_batches | 108 | 109 | 108 |
| production_lines | 1 | 1 | 1 |
| recommendations | 0 | 0 | 0 |
| sensor_readings | 373068 | 187875 | 31585 |
| sensors | 168 | 80 | 14 |
| simulation_scenarios | 0 | 0 | 0 |
| station_kpis | 84966 | 85428 | 85092 |
| station_types | 12 | 12 | 12 |
| stations | 42 | 42 | 42 |
| twin_context | 0 | 0 | 0 |
| vehicle_events | 93267 | 93822 | 92886 |
| vehicles | 2696 | 2717 | 2696 |

Counts were captured after generation and before training. SQL independently verified 12,185 passing station visits and 12,185 corresponding inspection records in the fourth full database. The prior audit recorded 568,553 total rows and 25.2 pipeline seconds. This release also writes the previously omitted tail of the inspection buffer. The corrected total is 568,883 (+330). The 1,389,326 generated events include raw sensor samples that collapse into per-visit aggregates.

Run from the repository root using a **new** directory. See [raw outputs](evidence/scenarios/results.json), [dependency versions](evidence/scenarios/requirements.freeze.txt) and [independent SQL counts](evidence/full-db-verification.json).

```sh
python scripts/reproduce_evidence.py --vehicles 2000 --seed 42 --full-runs 3 --mixed-runs 1 --output data/generated/my-experiment
python scripts/generate_data.py --scenario full --vehicles 2000 --seed 42 --db data/generated/plain-full.db
```

For publication, the scenario command arrays use `python` in place of the local interpreter's absolute profile path. The published hashes cover these portable copies. Numeric results are unchanged.
