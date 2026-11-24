# Reproducible TwinLine release

The public base commit `d914b2a908ec8cd5d18c5dfacc1ab71480ab4386` contained six files. The implementation comes from the corrected local audit of `TwinLine_Codex_Source.zip` (SHA-256 `190572b76d760aa94a811cfa8425cd9ab64fcb6bc330bccf81cfe7dc450f999a`). The previously deleted historical ZIP in public Git history was scanned for secrets and excluded as an implementation source.

- Restored the FastAPI, React, simulation, ingestion, model, migration, monitoring and test sources, including the prior sensor-count and Alembic corrections.
- Paired a passing inspection with its finalized visit, made failed ingestion roll back topology creation, and bound native numbers for PostgreSQL. Fixed Windows YAML decoding in the generator.
- Timed simulation, event dispatch, ETL and nested SQL cursor execution. Recorded fresh scenario databases, SQL counts and end-to-end clocks. Generated databases and model binaries stay outside Git.
- Removed the vehicle-list N+1 query. Cached four repeated SQLite read paths with transaction-sensitive freshness checks. Preserved response bodies on the comparison dataset.
- Purged unresolved training labels, moved split boundaries to decision time, excluded the retrospective anomaly-count feature, restricted anomaly scaling to early observations, enforced the validation alert budget and evaluated a frozen forest on a separate simulation seed. Scoped anomaly/prediction updates by line.
- Added four regression tests and separated the rate-limit test's client identity. Ran migrations on two database engines. Added fail-fast Compose startup, persistent model storage, loopback defaults and a Docker-enabled CI smoke test.
- Recorded a new browser walkthrough, exported charts and the ER diagram, documented uncertainty, and linked raw results.

[Release evidence](CLAIM_VERIFICATION.md) · [Limitations](docs/limitations.md)

