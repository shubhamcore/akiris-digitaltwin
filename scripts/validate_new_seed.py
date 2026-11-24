"""Evaluate a frozen model on a freshly simulated mixed line with a different seed."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, confusion_matrix, precision_score, recall_score, f1_score
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db.session import make_engine
from app.ml.features import build_vehicle_frame
from app.models import ModelVersion, ProductionLine

p = argparse.ArgumentParser(__doc__)
p.add_argument("training_db", type=Path)
p.add_argument("output", type=Path)
p.add_argument("--seed", default=137, type=int)
args = p.parse_args()
if args.output.exists() or not args.training_db.is_file():
    p.error("Supply an existing training database and new output file")
with Session(make_engine(f"sqlite:///{args.training_db.resolve().as_posix()}")) as session:
    mv = session.query(ModelVersion).filter_by(name="defect_risk").order_by(ModelVersion.id.desc()).first()
    threshold = mv.metrics["decision_threshold"]
    # Only load locally trained artifacts from the reproduction directory.
    artifact = joblib.load(mv.artifact_path)
with TemporaryDirectory() as tmp:
    db = Path(tmp) / "holdout.db"
    subprocess.run([sys.executable, "scripts/generate_data.py", "--vehicles", "2000", "--scenario", "mixed",
                    "--seed", str(args.seed), "--db", str(db)], cwd=ROOT, check=True)
    engine = make_engine(f"sqlite:///{db.as_posix()}")
    with Session(engine) as session:
        df, _ = build_vehicle_frame(session, session.query(ProductionLine.id).scalar())
    engine.dispose()
df = df[df.completed_at.notna() & df.as_of_time.notna()]
X = df.reindex(columns=artifact["cols"]).fillna(pd.Series(artifact["median"]))
p_hat = artifact["model"].predict_proba(X)[:,1]
alerts = p_hat >= threshold
y = df.label
tn, fp, fn, tp = confusion_matrix(y, alerts, labels=[0, 1]).ravel().tolist()
result = {"seed": args.seed, "training_seed": 42, "rows": len(y), "threshold": threshold,
          "prevalence": float(y.mean()), "roc_auc": roc_auc_score(y, p_hat),
          "average_precision": average_precision_score(y, p_hat), "alert_load": float(alerts.mean()),
          "precision": precision_score(y, alerts, zero_division=0), "recall": recall_score(y, alerts),
          "f1": f1_score(y, alerts), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
          "fpr": fp/(fp+tn), "fnr": fn/(fn+tp)}
args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

