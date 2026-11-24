# Claims supported by this release

| Claim | Evidence and scope |
|---|---|
| 42-station vehicle assembly simulation | Configured site, topology integration test and 42 station-quality rows per scenario. |
| 2,000 terminal vehicle outcomes | Full scenario, seed 42. 1,888 accepted plus 112 scrapped. Another 696 were still in progress. |
| 1,389,326 generated events | Identical in three instrumented repetitions and one untimed-by-stage repeat. Use **1.39M** when rounding or **1.38M+** as a lower bound. |
| 568,883 stored rows | SQL counts across application tables directly after ingestion. This fixes 330 omitted inspection passes compared with 568,553 in the prior audit. |
| Runtime | Three instrumented full runs had a 41.39 s pipeline median. A separate uninstrumented run took 38.34 s in the pipeline and 41.15 s for the CLI. The prior 25.2 s result belongs to the earlier code and environment. |
| 22 application tables | Reflected on SQLite and PostgreSQL 16.16, excluding Alembic bookkeeping. |
| 29 passing tests | Fresh locked Python environment. Includes the four new regression cases. |
| 60 concurrent simulated users | Same 60 s read-heavy Locust profile, one worker, local SQLite. Baseline 607 requests and 8.7 s p95. Optimized 8,502 requests, zero failures, 570 ms p95. The old 544-request test is historical. |
| Three sensor availability experiments | Mean station observability 0.934 / 0.669 / 0.436. These are instrumentation scores. |
| Evaluated ML prototype | Independent seed 137 had AP 0.0187 against prevalence 0.0197. Deployment value remains unproven. |

## Suggested resume wording

- **Backend/SWE** — Eliminated a per-vehicle prediction query and reused dashboard aggregates until SQLite data changed. Under the same 60-user Locust read workload, p95 latency fell from 8.7 s to 570 ms across 8,502 post-change requests with zero failures.
- **Data infrastructure** — Built a 42-station SimPy pipeline that turned 1,389,326 synthetic events into 568,883 relational rows for 2,000 terminal vehicle outcomes. Verified schema parity across 22 application tables in SQLite and PostgreSQL.
- **AI/robotics software** — Evaluated how sensor availability affects a simulated assembly line across 42 stations. Mean observability fell from 0.934 with full instrumentation to 0.669 with mixed coverage and 0.436 under brownfield conditions.

[Benchmark](docs/benchmark_report.md) · [Load test](docs/load_test_report.md) · [Station experiment](docs/observability_report.md) · [ML evaluation](docs/ml_evaluation_report.md) · [Testing](docs/testing_report.md) · [Schema](docs/database_schema.md)

