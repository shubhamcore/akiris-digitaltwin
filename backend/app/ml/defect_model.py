"""Defect-risk model — REAL training + honest metrics + DB-scored predictions.

V1: RandomForest (explainable importances, robust on tabular sensor stats and
class imbalance via balanced subsampling). Prediction confidence is a heuristic of margin and feature completeness. Extension points: CalibratedClassifierCV / conformal
prediction, per-sample SHAP explanations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (average_precision_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sqlalchemy.orm import Session

from ..models import Defect, ModelVersion, Prediction, Station, Vehicle
from . import registry
from .features import build_vehicle_frame

DROP_COLS = {"id", "label", "vin", "status", "quality_score", "line_id",
             "started_at", "completed_at", "batch_id", "t", "as_of_time",
             "upstream_anomaly_count"}


def _feature_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in DROP_COLS
            and df[c].dtype.kind in "ifbu"]


def _impute(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]):
    med = train[cols].median(numeric_only=True)
    return train[cols].fillna(med), test[cols].fillna(med), med


def train_defect_model(db: Session, line_id: int) -> dict:
    df, meta = build_vehicle_frame(db, line_id)
    if not df.empty:
        df = df[df.completed_at.notna() & df.as_of_time.notna()].copy()
    if len(df) < 10 or df.label.nunique() < 2:
        return {"error": "insufficient labeled data — generate more vehicles first",
                "rows": int(len(df))}
    df = df.sort_values(["as_of_time", "id"]).reset_index(drop=True)
    split = int(len(df) * 0.7)
    train, test = df.iloc[:split], df.iloc[split:]
    train = train[train.completed_at < test.as_of_time.iloc[0]]
    if len(train) < 8 or train.label.nunique() < 2:
        return {"error": "insufficient resolved outcomes before test window"}
    cols = _feature_cols(train)
    # The validation slice remains separate from the final fitted forest.

    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=3,
                                   class_weight="balanced_subsample", random_state=42,
                                   n_jobs=-1)
    # decision threshold chosen on an inner validation slice (never on test)
    inner = int(len(train) * 0.85)
    fit_df, val_df = train.iloc[:inner], train.iloc[inner:]
    fit_df = fit_df[fit_df.completed_at < val_df.as_of_time.iloc[0]]
    if fit_df.label.nunique() < 2:
        return {"error": "insufficient resolved outcomes before validation window"}
    Xfit, Xval, med = _impute(fit_df, val_df, cols)
    Xte = test[cols].fillna(med)
    model.fit(Xfit, fit_df.label)
    # threshold policy: max F1 subject to a sane alert load
    # (precision >= 0.25, matching what a floor team can actually work through);
    # fallback: flag the top ~5% risk shortlist
    val_p = model.predict_proba(Xval)[:, 1]
    best_thr = float(np.nextafter(np.quantile(val_p, 0.95, method="higher"), np.inf))
    if val_df.label.nunique() > 1:
        candidates = []
        for thr in np.arange(0.02, 0.9, 0.01):
            pred_v = (val_p >= thr).astype(int)
            p_v = precision_score(val_df.label, pred_v, zero_division=0)
            f1_v = f1_score(val_df.label, pred_v, zero_division=0)
            if pred_v.mean() <= 0.05 and pred_v.any() and p_v >= 0.25:
                candidates.append((f1_v, float(thr)))
        if candidates:
            _, best_thr = max(candidates)
    # Freeze both the fitted forest and validation-selected threshold.
    proba = model.predict_proba(Xte)[:, 1]
    pred = (proba >= best_thr).astype(int)
    y = test.label.to_numpy()
    fp = int(((pred == 1) & (y == 0)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tp = int(((pred == 1) & (y == 1)).sum())
    metrics = {
        "precision": round(precision_score(y, pred, zero_division=0), 3),
        "recall": round(recall_score(y, pred, zero_division=0), 3),
        "f1": round(f1_score(y, pred, zero_division=0), 3),
        "fpr": round(fp / max(fp + tn, 1), 3),
        "fnr": round(fn / max(fn + tp, 1), 3),
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "roc_auc": round(roc_auc_score(y, proba), 3) if len(np.unique(y)) > 1 else None,
        "pr_auc": round(average_precision_score(y, proba), 4) if len(np.unique(y)) > 1 else None,
        "flag_rate_at_threshold": round(float((proba >= best_thr).mean()), 4),
        "train_rows": int(len(train)), "test_rows": int(len(test)),
        "positives_rate": round(float(df.label.mean()), 4),
        "decision_threshold": float(best_thr), "validation_alert_load": float((val_p >= best_thr).mean()),
        "threshold_note": "decision threshold tuned on inner validation slice (never on test)",
        "split": "chronological decision time, 70/30 boundary; purge unresolved training labels",
        "test_positives": int(y.sum()), "fit_rows": len(fit_df), "validation_rows": len(val_df),
        "majority_baseline": {"precision": 0, "recall": 0, "f1": 0, "alert_load": 0,
                              "pr_auc": round(float(y.mean()), 4), "roc_auc": 0.5 if len(set(y)) > 1 else None},
        "all_alert_baseline": {"precision": round(float(y.mean()), 4), "recall": 1 if y.any() else 0,
                               "f1": round(float(2*y.mean()/(1+y.mean())), 4), "alert_load": 1},
        "fit_latest_outcome": float(fit_df.completed_at.max()),
        "validation_first_decision": float(val_df.as_of_time.min()),
        "train_latest_outcome": float(train.completed_at.max()),
        "test_first_decision": float(test.as_of_time.min()),
    }
    importances = sorted(zip(cols, model.feature_importances_),
                         key=lambda kv: -kv[1])
    metrics["top_features"] = [{"feature": f, "importance": round(float(i), 4)}
                               for f, i in importances[:8]]
    mv = registry.save_model(db, {"model": model, "cols": cols, "median": med.to_dict()},
                             name="defect_risk", algo="RandomForestClassifier",
                             metrics=metrics,
                             notes=f"as_of_seq={meta['as_of_seq']} (end of paint)")
    return {"model_version": mv.version, "metrics": metrics}


def score_vehicles(db: Session, line_id: int, mv_id: int | None = None) -> dict:
    mv, artifact = registry.load_latest(db, "defect_risk")
    if mv is None:
        return {"error": "no defect_risk model trained yet"}
    df, meta = build_vehicle_frame(db, line_id)
    if df.empty:
        return {"error": "no scorable vehicles"}
    cols = artifact["cols"]
    X = df.reindex(columns=cols).fillna(pd.Series(artifact["median"]))
    proba = artifact["model"].predict_proba(X)[:, 1]
    margin = np.abs(proba - 0.5) * 2.0
    confidence = np.clip(0.30 + 0.45 * df["completeness"].to_numpy() + 0.35 * margin,
                         0.05, 0.99)
    top = [{"feature": t["feature"], "importance": t["importance"]}
           for t in mv.metrics.get("top_features", [])[:5]]

    db.query(Prediction).filter(Prediction.model_version_id == mv.id, Prediction.vehicle_id.in_(
        db.query(Vehicle.id).filter(Vehicle.line_id == line_id))).delete(synchronize_session=False)
    rows = []
    for (_, veh), p, c in zip(df.iterrows(), proba, confidence):
        rows.append({"vehicle_id": int(veh.id), "model_version_id": mv.id,
                     "created_at": float(veh.as_of_time or veh.started_at),
                     "as_of_seq": int(meta["as_of_seq"]),
                     "defect_probability": round(float(p), 4),
                     "confidence": round(float(c), 3),
                     "data_completeness": round(float(veh.completeness), 3),
                     "top_features": top})
        if len(rows) >= 2000:
            db.bulk_insert_mappings(Prediction, rows)
            rows = []
    if rows:
        db.bulk_insert_mappings(Prediction, rows)
    db.commit()
    n = resolve_predictions(db, line_id)
    return {"scored": len(df), "resolved": n, "model_version": mv.version}


def resolve_predictions(db: Session, line_id: int) -> int:
    """Attach actual outcomes (the trust/validation loop of the PS)."""
    station_seq = dict(db.query(Station.id, Station.seq)
                       .filter(Station.line_id == line_id).all())
    defect_seq = {d.vehicle_id: station_seq.get(d.station_id, 0)
                  for d in db.query(Defect).all()}
    veh_status = dict(db.query(Vehicle.id, Vehicle.status)
                      .filter(Vehicle.line_id == line_id).all())
    n = 0
    pending = db.query(Prediction).filter(Prediction.outcome.is_(None)).all()
    thresholds: dict[int, float] = {}
    for p in pending:
        if p.model_version_id not in thresholds:
            mv = db.get(ModelVersion, p.model_version_id)
            thresholds[p.model_version_id] = (
                mv.metrics.get("decision_threshold", 0.5) if mv else 0.5)
        thr = thresholds[p.model_version_id]
        veh_id = p.vehicle_id
        status = veh_status.get(veh_id)
        if status not in ("completed", "scrapped"):
            continue
        failed_later = defect_seq.get(veh_id, -1) > p.as_of_seq
        p.outcome = bool(failed_later)
        p.correct = bool((p.defect_probability >= thr) == p.outcome)
        n += 1
    db.commit()
    return n
