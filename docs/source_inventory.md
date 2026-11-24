# Source inventory

Paths are relative to the repository root. The release restores the implementation from the audited authoritative source. The runtime uses backend/tests, config files under configs, the load profile under load, and a sample under data/sample. Full generated databases, fitted models, node_modules, build outputs and failed scratch runs are excluded.

## API surface

| Method | Path | Handler |
|---|---|---|
| GET | `/bottlenecks` | `routes_analytics.bottlenecks` |
| GET | `/observability/advisor` | `routes_analytics.observability_advisor` |
| GET | `/contributing-factors/patterns` | `routes_analytics.contributing_patterns` |
| GET | `/contributing-factors/{station_ident}` | `routes_analytics.contributing_factors_station` |
| GET | `/contributing-factors/vehicle/{vehicle_id}` | `routes_analytics.contributing_factors_vehicle` |
| GET | `/evidence-matrix/{station_ident}` | `routes_analytics.evidence_matrix_endpoint` |
| GET | `/anomalies` | `routes_analytics.anomalies` |
| GET | `/defect-risks` | `routes_analytics.defect_risks` |
| GET | `/predictions` | `routes_analytics.predictions` |
| GET | `/model-performance` | `routes_analytics.model_performance` |
| GET | `/shadow/changes` | `routes_analytics.shadow_proposed_changes` |
| GET | `/shadow/windows` | `routes_analytics.shadow_windows` |
| GET | `/shadow/scenarios` | `routes_analytics.shadow_scenarios` |
| POST | `/shadow/scenarios` | `routes_analytics.shadow_create_scenario` |
| GET | `/shadow/scenarios/{scenario_id}` | `routes_analytics.shadow_scenario_detail` |
| POST | `/shadow/scenarios/{scenario_id}/run` | `routes_analytics.shadow_run` |
| POST | `/shadow/scenarios/{scenario_id}/status` | `routes_analytics.shadow_status` |
| POST | `/shadow/scenarios/{scenario_id}/queue` | `routes_analytics.shadow_queue` |
| GET | `/shadow/queue` | `routes_analytics.shadow_queue_view` |
| GET | `/defects` | `routes_analytics.defects_list` |
| GET | `/defects/{defect_id}/trace` | `routes_analytics.defect_trace` |
| GET | `/predictions/trust` | `routes_analytics.prediction_trust_view` |
| POST | `/predictions/trust/revalidate` | `routes_analytics.prediction_revalidate_view` |
| POST | `/predictions/trust/retrain` | `routes_analytics.prediction_retrain_view` |
| POST | `/predictions/trust/approve` | `routes_analytics.prediction_approve_view` |
| POST | `/predictions/trust/deploy` | `routes_analytics.prediction_deploy_view` |
| GET | `/recommendations` | `routes_analytics.recommendations` |
| GET | `` | `routes_factory.list_factories` |
| GET | `/active` | `routes_factory.active_factory` |
| POST | `` | `routes_factory.create_factory` |
| GET | `/{factory_id}` | `routes_factory.factory_detail` |
| POST | `/{factory_id}/activate` | `routes_factory.activate` |
| POST | `/{factory_id}/simulate` | `routes_factory.simulate` |
| GET | `/vehicles` | `routes_fleet.list_vehicles` |
| GET | `/vehicles/{vehicle_id}/journey` | `routes_fleet.journey` |
| GET | `/vehicles/{vehicle_id}/contributing-factors` | `routes_fleet.contributing_factors` |
| GET | `/inspections` | `routes_fleet.list_inspections` |
| GET | `/plants` | `routes_meta.list_plants` |
| GET | `/lines` | `routes_meta.list_lines` |
| GET | `/stations` | `routes_meta.list_stations` |
| GET | `/stations/{station_id}` | `routes_meta.station_detail` |
| GET | `/data-quality` | `routes_meta.data_quality` |
| POST | `/simulation/run` | `routes_ops.run_simulation` |
| POST | `/data/ingest` | `routes_ops.ingest_file` |
| POST | `/ml/refresh` | `routes_ops.ml_refresh` |
| GET | `/injection/kinds` | `routes_ops.injection_kinds` |
| POST | `/injection/inject` | `routes_ops.inject` |
| GET | `/production/summary` | `routes_production.summary` |
| GET | `/production/roi` | `routes_production.roi` |
| GET | `/production/trends` | `routes_production.trends` |
| GET | `/` | `main.root` |
| GET | `/health` | `main.health` |
| GET | `/ready` | `main.ready` |
| GET | `/metrics` | `main.metrics` |

The framework also serves OpenAPI and interactive documentation.

## File inventory

| Path | Role |
|---|---|
| `.dockerignore` | Project configuration or dependency manifest |
| `.env.example` | Project configuration or dependency manifest |
| `.gitattributes` | Project configuration or dependency manifest |
| `.github/workflows/ci.yml` | CI workflow |
| `.github/workflows/compose.yml` | CI workflow |
| `.gitignore` | Project configuration or dependency manifest |
| `CLAIM_VERIFICATION.md` | Documentation |
| `INNOVATIONS_SUMMARY.md` | Documentation |
| `README.md` | Documentation |
| `RELEASE_NOTES.md` | Documentation |
| `RUN_ME.md` | Documentation |
| `backend/alembic.ini` | Project configuration or dependency manifest |
| `backend/alembic/env.py` | Alembic environment: target metadata from app.db.session.Base, database |
| `backend/alembic/script.py.mako` | Project configuration or dependency manifest |
| `backend/alembic/versions/20261124_01_align_factory_and_model_lifecycle_schema.py` | align factory and model lifecycle schema |
| `backend/alembic/versions/803153c85c70_initial_schema.py` | initial schema |
| `backend/app/__init__.py` | Python package initializer |
| `backend/app/api/__init__.py` | Python package initializer |
| `backend/app/api/deps.py` | Shared API dependencies + helpers. |
| `backend/app/api/routes_analytics.py` | Analytics endpoints: bottlenecks, anomalies, defect risks, predictions, |
| `backend/app/api/routes_factory.py` | Factory Setup API — configure any factory, then use it as the Digital Twin. |
| `backend/app/api/routes_fleet.py` | Vehicle fleet + genealogy endpoints. |
| `backend/app/api/routes_meta.py` | Topology + observability endpoints. |
| `backend/app/api/routes_ops.py` | Ops endpoints: run simulation, ingest files, refresh ML/analytics. |
| `backend/app/api/routes_production.py` | Production + business endpoints. |
| `backend/app/config/__init__.py` | Python package initializer |
| `backend/app/core/__init__.py` | Python package initializer |
| `backend/app/core/config.py` | Central configuration — every value env-overridable (req: env-based config). |
| `backend/app/core/metrics.py` | Prometheus instrumentation: HTTP counters/histograms + twin-state gauges. |
| `backend/app/core/rate_limit.py` | Per-IP token-bucket rate limiting for MUTATING methods (POST/PUT/DELETE). |
| `backend/app/db/__init__.py` | Python package initializer |
| `backend/app/db/session.py` | Engine/session factory. Same models run on SQLite (local) or PostgreSQL (docker). |
| `backend/app/ingestion/__init__.py` | Python package initializer |
| `backend/app/ingestion/base.py` | DataSource abstraction — the seam for future PLC / OPC-UA / MQTT / MES feeds. |
| `backend/app/ingestion/csv_source.py` | CSVDataSource — replays a previously recorded event log (JSONL or CSV). |
| `backend/app/ingestion/pipeline.py` | IngestionPipeline: normalized event stream  ->  relational digital twin state. |
| `backend/app/ingestion/simulator_source.py` | SimulatorDataSource — drives the SimPy assembly-line engine and streams its |
| `backend/app/main.py` | TwinLine Digital Twin — FastAPI entrypoint. |
| `backend/app/ml/__init__.py` | Python package initializer |
| `backend/app/ml/anomaly.py` | Anomaly detection — IsolationForest per sensor profile (stations with the |
| `backend/app/ml/defect_model.py` | Defect-risk model — REAL training + honest metrics + DB-scored predictions. |
| `backend/app/ml/features.py` | Feature engineering for defect-risk prediction. |
| `backend/app/ml/registry.py` | Model registry — artifacts on disk, versions + metrics in DB (model_versions). |
| `backend/app/models/__init__.py` | Python package initializer |
| `backend/app/models/analytics.py` | Analytics entities: anomalies, predictions (+outcome resolution for trust), |
| `backend/app/models/core_entities.py` | Twin topology: Plant -> ProductionLine -> Station (+StationType, Sensor). |
| `backend/app/models/production.py` | Production execution entities: batches, vehicles, events, readings, |
| `backend/app/schemas/__init__.py` | Python package initializer |
| `backend/app/schemas/payloads.py` | Request payloads (POST bodies) — validated at the edge. |
| `backend/app/services/__init__.py` | Python package initializer |
| `backend/app/services/bottleneck.py` | Bottleneck service — V1 heuristic score over real evidence. |
| `backend/app/services/business.py` | Business / ROI service — configurable assumptions, auditable math. |
| `backend/app/services/contributing_factors.py` | Multi-causal contributing-factor analysis (Innovation 2). |
| `backend/app/services/data_quality.py` | Data-quality / observability service. |
| `backend/app/services/defect_traceback.py` | Defect traceback & propagation analysis (Innovation 4). |
| `backend/app/services/factory_config.py` | Factory Setup — configure-any-factory workflow. |
| `backend/app/services/genealogy.py` | Genealogy (digital thread) + root-cause ranking. |
| `backend/app/services/injection.py` | Scenario injection layer — LIVE TWIN CONTINUATION for demos and drills. |
| `backend/app/services/observability_advisor.py` | Observability Advisor — turns passive coverage/confidence monitoring into an |
| `backend/app/services/prediction_trust.py` | Prediction validation & AI trust (Innovation 5). |
| `backend/app/services/read_snapshot.py` | Reuse read-only SQLite dashboard aggregates while their source is unchanged. |
| `backend/app/services/recommendations.py` | Recommendation engine — advisory only (read-only / shadow-mode twin). |
| `backend/app/services/shadow_sim.py` | Safe change validation + shadow simulation (Innovation 3). |
| `backend/app/services/twin_state.py` | Twin state service — the 'digital twin' snapshot each persona view reads from. |
| `backend/app/simulation/__init__.py` | Python package initializer |
| `backend/app/simulation/emit.py` | Event sink: JSONL always; MQTT/Sparkplug-style topics when a broker is reachable. |
| `backend/app/simulation/engine.py` | Discrete-event assembly-line engine (SimPy). |
| `backend/app/simulation/mechanisms.py` | The four causal defect mechanisms from the solution design. |
| `backend/app/simulation/part.py` | Part model with full process genealogy (digital thread). |
| `backend/requirements.lock` | Project configuration or dependency manifest |
| `backend/requirements.txt` | Project configuration or dependency manifest |
| `backend/tests/__init__.py` | Python package initializer |
| `backend/tests/conftest.py` | Test fixtures: build a small twin database once per session (60 vehicles), |
| `backend/tests/test_api.py` | API + ML-refresh tests (against the 60-vehicle session fixture DB). |
| `backend/tests/test_factory_setup.py` | Factory Setup — configure-any-factory (backend tests). |
| `backend/tests/test_pipeline.py` | Data-generation / genealogy / bottleneck / missing-data tests. |
| `backend/tests/test_release.py` | test_every_inspection_visit_has_one_matching_result, test_snapshot_invalidates_after_external_and_same_connection_writes, test_failed_stream_rolls_back_topology, test_migration_roundtrip |
| `configs/automotive_line.yaml` | Simulator configuration |
| `configs/scenarios/brownfield.yaml` | Simulator configuration |
| `configs/scenarios/full.yaml` | Simulator configuration |
| `data/sample/README.md` | Checked-in synthetic sample or its documentation |
| `data/sample/twin_excerpt.json` | Checked-in synthetic sample or its documentation |
| `docker-compose.yml` | Project configuration or dependency manifest |
| `docker/backend.Dockerfile` | Image or monitoring configuration |
| `docker/frontend.Dockerfile` | Image or monitoring configuration |
| `docker/grafana/provisioning/dashboards/dashboards.yml` | Image or monitoring configuration |
| `docker/grafana/provisioning/dashboards/twinline_ops.json` | Image or monitoring configuration |
| `docker/grafana/provisioning/datasources/prometheus.yml` | Image or monitoring configuration |
| `docker/prometheus/prometheus.yml` | Image or monitoring configuration |
| `docs/architecture.md` | Documentation |
| `docs/benchmark_report.md` | Documentation |
| `docs/database_schema.md` | Documentation |
| `docs/demo_walkthrough.md` | Documentation |
| `docs/docker_verification.md` | Documentation |
| `docs/evidence/baseline/api.log` | Measured evidence or reproducibility input |
| `docs/evidence/baseline/execution.log` | Measured evidence or reproducibility input |
| `docs/evidence/baseline/locust_exceptions.csv` | Measured evidence or reproducibility input |
| `docs/evidence/baseline/locust_failures.csv` | Measured evidence or reproducibility input |
| `docs/evidence/baseline/locust_stats.csv` | Measured evidence or reproducibility input |
| `docs/evidence/baseline/locust_stats_history.csv` | Measured evidence or reproducibility input |
| `docs/evidence/clean-clone-pytest.xml` | Measured evidence or reproducibility input |
| `docs/evidence/clean-generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/clean-training.log` | Measured evidence or reproducibility input |
| `docs/evidence/clone-frontend-build.log` | Measured evidence or reproducibility input |
| `docs/evidence/frontend-build.log` | Measured evidence or reproducibility input |
| `docs/evidence/full-db-verification.json` | Measured evidence or reproducibility input |
| `docs/evidence/independent-ml.json` | Measured evidence or reproducibility input |
| `docs/evidence/npm-audit.json` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/api.log` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/execution.log` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/locust_exceptions.csv` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/locust_failures.csv` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/locust_stats.csv` | Measured evidence or reproducibility input |
| `docs/evidence/optimized/locust_stats_history.csv` | Measured evidence or reproducibility input |
| `docs/evidence/postgres-final.log` | Measured evidence or reproducibility input |
| `docs/evidence/postgres-schema.json` | Measured evidence or reproducibility input |
| `docs/evidence/profile-after.json` | Measured evidence or reproducibility input |
| `docs/evidence/profile-before.json` | Measured evidence or reproducibility input |
| `docs/evidence/pytest-audit.xml` | Measured evidence or reproducibility input |
| `docs/evidence/pytest.xml` | Measured evidence or reproducibility input |
| `docs/evidence/python-audit.json` | Measured evidence or reproducibility input |
| `docs/evidence/restore-baseline.patch` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/brownfield_1_generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/brownfield_1_training.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/environment.json` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/full_1_generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/full_1_training.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/full_2_generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/full_3_generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/mixed_1_generation.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/mixed_1_training.log` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/requirements.freeze.txt` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/results.json` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/sha256.json` | Measured evidence or reproducibility input |
| `docs/evidence/scenarios/stations.csv` | Measured evidence or reproducibility input |
| `docs/evidence/sqlite-schema.json` | Measured evidence or reproducibility input |
| `docs/evidence/uninstrumented-time.json` | Measured evidence or reproducibility input |
| `docs/evidence/uninstrumented.log` | Measured evidence or reproducibility input |
| `docs/limitations.md` | Documentation |
| `docs/load_test_report.md` | Documentation |
| `docs/ml_evaluation_report.md` | Documentation |
| `docs/observability.svg` | Project configuration or dependency manifest |
| `docs/observability_report.md` | Documentation |
| `docs/scenario_report.md` | Documentation |
| `docs/screenshots/leadership.png` | Observed dashboard capture |
| `docs/screenshots/manager.png` | Observed dashboard capture |
| `docs/screenshots/supervisor.png` | Observed dashboard capture |
| `docs/screenshots/walkthrough.mp4` | Observed dashboard capture |
| `docs/security_audit.md` | Documentation |
| `docs/source_inventory.md` | Documentation |
| `docs/test_execution_report.md` | Documentation |
| `docs/testing_report.md` | Documentation |
| `frontend/index.html` | Project configuration or dependency manifest |
| `frontend/package-lock.json` | Project configuration or dependency manifest |
| `frontend/package.json` | Project configuration or dependency manifest |
| `frontend/postcss.config.js` | Project configuration or dependency manifest |
| `frontend/src/App.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/CFAnalysis.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/DefectTraceback.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/FactorySetup.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/ObsAdvisor.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/PredictionTrust.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/ShadowSim.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/StationDrawer.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/VehiclePanel.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/api.ts` | React/TypeScript UI module or stylesheet |
| `frontend/src/components.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/index.css` | React/TypeScript UI module or stylesheet |
| `frontend/src/main.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/pages/Leadership.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/pages/Manager.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/src/pages/Supervisor.tsx` | React/TypeScript UI module or stylesheet |
| `frontend/tailwind.config.js` | Project configuration or dependency manifest |
| `frontend/tsconfig.json` | Project configuration or dependency manifest |
| `frontend/vite.config.ts` | Project configuration or dependency manifest |
| `load/locustfile.py` | Locust load test for the TwinLine read path. |
| `scripts/bootstrap.sh` | Project configuration or dependency manifest |
| `scripts/export_sample.py` | Export a small checked-in sample of the generated twin for reviewers. |
| `scripts/generate_data.py` | Build the digital-twin database from a DataSource (simulator by default). |
| `scripts/measure_load.py` | Run the existing 60-user profile on a private copy of a synthetic SQLite snapshot. |
| `scripts/profile_reads.py` | Count SQL calls and time real responses for the dashboard read paths. |
| `scripts/reproduce_evidence.py` | Rebuild synthetic data and record generation, schema and model evidence. |
| `scripts/run_sim.py` | Run the assembly-line simulator and write a replayable event log. |
| `scripts/seed_if_empty.py` | Container startup after Alembic migration. Preserve populated demo volumes. |
| `scripts/test_postgres.ps1` | Project configuration or dependency manifest |
| `scripts/train_models.py` | Train/evaluate models + refresh analytics (CLI equivalent of POST /ml/refresh). |
| `scripts/validate_new_seed.py` | Evaluate a frozen model on a freshly simulated mixed line with a different seed. |
| `scripts/verify_schema.py` | Inspect a migrated database. Accepts TWIN_DATABASE_URL via application settings. |

## Reconciliation

Original archive files absent from this release: data/models/defect_risk_v1.0_20260829062417.joblib, data/models/defect_risk_v1.0_20260829064219.joblib, data/models/defect_risk_v1.0_20260829065622.joblib, data/models/defect_risk_v1.0_20260829070331.joblib, data/models/defect_risk_v1.0_20260829070533.joblib, data/models/defect_risk_v1.0_20260829070651.joblib, data/models/defect_risk_v1.0_20260829070827.joblib, data/models/defect_risk_v1.0_20260829072418.joblib, data/models/defect_risk_v1.0_20260829072532.joblib, data/models/defect_risk_v1.0_20260829093613.joblib, data/models/defect_risk_v1.0_20260829093738.joblib, data/models/defect_risk_v1.0_20260829094441.joblib, data/models/defect_risk_v1.0_20260829140117.joblib, data/models/defect_risk_v1.0_20260829140239.joblib, data/models/defect_risk_v1.0_20260830052252.joblib, data/models/defect_risk_v1.0_20260830052351.joblib, data/models/defect_risk_v1.0_20260830052416.joblib, data/models/defect_risk_v1.0_20260830052458.joblib, data/models/defect_risk_v1.0_20260830052519.joblib, data/models/defect_risk_v1.0_20260830052843.joblib, data/models/defect_risk_v1.0_20260830052920.joblib, data/models/defect_risk_v1.0_20260830053021.joblib, data/models/defect_risk_v1.0_20260830053613.joblib, data/models/defect_risk_v1.0_20260830054225.joblib. Historical development notes are marked as such. The supplied synthetic sample remains a format example. npm package-lock.json drives the tested npm and Docker build; the previous audit's pnpm lock was retired when the npm lock was updated. The raw event exporter and replay adapter are independent entry points. A live MES, physical-line integration and production deployment are absent. Docker is tracked separately in the container report.
