"""Container startup after Alembic migration. Preserve populated demo volumes."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db.session import SessionLocal
from app.models import ProductionLine, Vehicle

with SessionLocal() as session:
    populated = session.query(Vehicle.id).first() is not None
    provisioned = session.query(ProductionLine.id).first() is not None
if not populated and not provisioned:
    subprocess.run([sys.executable, "scripts/generate_data.py", "--scenario", os.getenv("TWIN_SCENARIO", "mixed"),
                    "--vehicles", os.getenv("TWIN_SEED_VEHICLES", "1500"), "--seed",
                    os.getenv("TWIN_DEFAULT_SEED", "42")], cwd=ROOT, check=True)
    populated = True
if populated:
    with SessionLocal() as session:
        from app.models import ModelVersion
        latest = session.query(ModelVersion).filter_by(name="defect_risk").order_by(ModelVersion.id.desc()).first()
        has_artifact = bool(latest and Path(latest.artifact_path).is_file())
    if not has_artifact:
        subprocess.run([sys.executable, "scripts/train_models.py"], cwd=ROOT, check=True)

