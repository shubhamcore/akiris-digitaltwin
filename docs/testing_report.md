# Automated verification

A fresh Python 3.12.14 virtual environment installed the pinned backend lockfile. Pytest collected **29 cases**, passed all 29 in 41.12 seconds, with one Starlette/httpx TestClient deprecation warning. The original archive contained 24 cases. The earlier audit added sensor-count coverage. This release adds four tests for inspection completeness, interrupted-ingestion rollback, cache freshness and migration round trips. [Final JUnit result](evidence/pytest.xml)

An intermediate run passed 28 of 29. A rate-limit test reused the next test's client bucket, intermittently producing 429 instead of the expected 422 for an invalid payload. The rate-limit test now has its own client identity. Both the throttling and invalid-input assertions remain in place. [Intermediate result](evidence/pytest-audit.xml)

The suite exercises FastAPI responses, required error conditions, configured factory provisioning, SimPy generation, genealogy, ingestion, analytics and migration behavior. The SQLite round trip compares metadata, indexes, primary keys and foreign-key integrity and verifies a populated model row survives the migration. The separate PostgreSQL smoke covers actual driver binding. The source contains no dedicated frontend component-unit suite. A clean npm ci installed 224 packages, then TypeScript and Vite 7.3.8 built 704 modules. The primary JS bundle was 731.83 kB (203.31 kB gzip); Vite emitted a bundle-size warning. A running UI walkthrough exercised the three persona views.

```sh
python -m pytest backend/tests -q
cd frontend
npm ci
npm run build
```

Push and pull-request workflows run pytest, frontend build, dependency audits and the Compose integration job. Each command propagates its exit code.

A separate local Git clone of the release branch passed all 29 cases in 68.77 seconds. [Clean checkout result](evidence/clean-clone-pytest.xml) · [Final frontend build log](evidence/frontend-build.log)

The clean local checkout also completed the documented SQLite migration, 2,000-terminal-outcome mixed generation, training, offline npm ci and production build. [Generation](evidence/clean-generation.log) · [Training](evidence/clean-training.log) · [Frontend](evidence/clone-frontend-build.log). This clone run was a functionality check on a busy desktop.
