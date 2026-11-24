# Known limitations

- All factory observations and business scenarios are simulated. The application offers retrospective decision support. It has no validated physical-control loop.
- The synthetic defect model underperformed a constant ranking on independent seed 137. Feature and threshold choices need validation on independent labeled manufacturing data before operational use. Alert rates shift between windows. Isolation Forest scores have no labeled anomaly validation.
- Station observability is an uncalibrated policy score. Manual stations receive a defined completeness contribution even when they lack sensors. Site-wide environmental observations and a global simulation clock limit isolation across factories with different timelines.
- The seeded load test describes a repeated-read workload on Windows SQLite. The tested read cache is SQLite-specific. Frequent commits invalidate cached summaries. PostgreSQL latency, WAN traffic, distributed workers and concurrent writes were not benchmarked.
- The summary UI's FPY uses all spawned vehicles, including work in progress. Trend buckets use finished vehicles. Compare explicit accepted/scrapped counts where the denominator matters.
- The Vite development server is used in the Compose demo. The demo includes state-changing endpoints. Keep it loopback-bound and configure access control for shared use. Use self-generated model artifacts.
- A large frontend bundle, a TestClient deprecation warning and long dashboard panels remain. The initial historical screenshot used an incorrectly decoded factory name; the generator now reads YAML as UTF-8.
