# API read performance

One Windows desktop, one Uvicorn worker and Locust 2.47.0 on loopback, 60 users, 15 spawned per second, 60 seconds requested, 50–300 ms user think time. Both runs used private SQLite backups of the identical previously trained seed-42 mixed database. The dashboard endpoints, weighted tasks, number of workers, duration, think time and response data stayed fixed. One sequence per build; task choice and scheduling vary. A separate single-client profiler ran alongside each workload. The startup probe and in-flight completions also appear in server logs.

| Final Locust console metric | Before | After |
|---|---|---|
| Requests | 607 | 8502 |
| Successful | 607 | 8502 |
| Failed | 0 | 0 |
| Requests/s | 10.28 | 144.28 |
| p50 ms | 5300 | 160 |
| p95 ms | 8700 | 570 |
| p99 ms | 9300 | 1600 |

## Endpoint-specific latency

Server-side p50 / p95 / p99 milliseconds, grouped from all successful access-log entries including dynamic vehicle IDs. Client-side endpoint statistics, errors, periodic snapshots and final console summaries are retained in the [before](evidence/baseline/) and [after](evidence/optimized/) directories. Server times omit client networking and some response delivery. The final console count can exceed the last periodic CSV snapshot.

| Route | Before ms | After ms |
|---|---|---|
| /bottlenecks | 6762 / 9139 / 10058 | 128 / 424 / 1954 |
| /defect-risks | 4256 / 6924 / 8607 | 256 / 580 / 827 |
| /health | 705 / 2347 / 2887 | 13 / 46 / 119 |
| /production/summary | 4417 / 6344 / 7309 | 124 / 400 / 690 |
| /production/trends | 7130 / 9344 / 9811 | 130 / 501 / 2671 |
| /stations | 6812 / 8547 / 8860 | 126 / 432 / 1905 |
| /vehicles | 2387 / 5171 / 7041 | 456 / 2207 / 2624 |
| /vehicles/{id}/journey | 4298 / 6231 / 8214 | 390 / 800 / 1249 |

## SQL and freshness

| Single-client path | Before SQL calls | After SQL calls | Identical response digest |
|---|---|---|---|
| /vehicles?limit=200 | 203 | 4 | yes |
| /stations | 10 | 12 | yes |
| /bottlenecks | 7 | 9 | yes |
| /production/summary | 9 | 11 | yes |
| /production/trends?bucket_vehicles=50 | 3 | 5 | yes |
| /defect-risks?threshold=0.4&limit=40 | 3 | 3 | yes |
| /vehicles/2520/journey | 7 | 7 | yes |
| /health | 0 | 0 | yes |

The fleet read fetched the latest prediction once per vehicle. A batched read now selects the newest prediction per candidate with deterministic tie ordering. Four repeated dashboard reads now reuse the real computed response on an unchanged SQLite connection. A bounded 32-entry LRU per pooled connection keys each result by line and request arguments. SQLite data version, schema version and total changes catch external commits, local DML and DDL. The code checks state before and after a miss, bypasses open write transactions and keeps the uncached path for PostgreSQL. There is no clock-based TTL. A regression exercises external commits, same-connection writes and rollback. The [baseline profile](evidence/profile-before.json) and [revised profile](evidence/profile-after.json) contain SQL shapes and payload hashes. The latter is a cold single read, so cold snapshot computation adds two version checks.

Cold bottleneck and station reads still group large history tables. The trend endpoint still materializes finished-vehicle observations in pandas. SQLite connection-pool occupancy, Python serialization, CPU contention and cold starts remain relevant. No pool expansion or new index was needed for the demonstrated read-only case. The frontend polls several views at 15–60 second intervals with React Query. The test is more aggressive and does not measure sustained mutation traffic, cache churn, multiworker deployments or PostgreSQL latency. The original 544-request run at 11-second p95 is historical evidence from a different session.

To repeat on a fresh generated and trained mixed database, run from the repository root. Each invocation starts a private single-worker API, backs up the supplied SQLite database, runs the same Locust file and preserves the final console log and periodic CSVs.

```sh
python scripts/measure_load.py data/generated/my-experiment/mixed_1.db data/generated/load-check
```

To reconstruct the previous data/route implementations, apply `git apply docs/evidence/restore-baseline.patch` in a separate disposable checkout. Generate and train a fresh mixed seed-42 database with 2,000 finished vehicles there. Supply that same database to both builds of the load runner. Raw request counts and latencies vary per run.
