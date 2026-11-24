# Docker Compose verification

GitHub Actions successfully built and ran the Compose stack on Ubuntu for commit 0a9081c1bd2319d2c93942d126ae7c94f4b64cda. The Windows audit host had no Docker CLI or engine. PostgreSQL 16.16 did run natively, including a clean migration round trip, schema reflection and a 60-terminal-outcome simulation. A clean npm build and local Vite/FastAPI UI capture also succeeded. Those are separate checks. The Docker-enabled runner passed image builds, health checks, Alembic schema comparison, frontend API proxy, 42-station topology, 100 terminal outcomes and a persistent-volume restart. [Successful Compose run](https://github.com/shubhamcore/akiris-digitaltwin/actions/runs/45349495171)

The [Compose workflow](../.github/workflows/compose.yml) builds both Dockerfiles on Ubuntu, starts a healthy PostgreSQL 16 service, applies migrations, checks backend readiness, verifies frontend HTML and an API proxy request, checks the 42-station topology and 100 finished vehicles, and recreates containers against persistent volumes. The workflow fails on build, readiness, migration or data assertion errors.

Startup propagates generation failures. The local demo binds published ports to loopback, uses a user-supplied PostgreSQL password, and stores trained models and database state on separate named volumes. On an existing volume from a pre-Alembic deployment, inspect schema history and back up data before attempting migration. No unattended conversion of an unversioned legacy database was tested.

