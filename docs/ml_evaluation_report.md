# Defect risk and anomaly evaluation

Predict a defect **after paint** for vehicles that reached the decision point. Train and evaluate on resolved outcomes. WIP remains eligible for scoring. Simulation truth, vehicle status, quality score and future outcomes are excluded from inputs. Features include upstream cycle deviations, sensor aggregates or missing indicators, environmental context, prior batch outcomes and backward-looking line history. The full-data upstream anomaly count was removed from the classifier. Its preprocessing and fit window could cross earlier decisions. The Isolation Forest remains available for retrospective anomaly analysis.

Chronological prediction-time order, 70% boundary, with unresolved labels purged at the boundary. The earlier window is divided chronologically into fit and validation. Fit labels must resolve before validation begins. The forest and median imputers are fitted only on that earlier fit slice. An alert threshold is chosen on validation by maximum F1 subject to precision ≥ 0.25 and alert load ≤ 5%, falling back to the upper validation tail. The fitted model and threshold are frozen before the final time slice. The 5% validation limit does not guarantee future workload. Each scenario fits a separate model.

| Scenario | Test n | Positives | Precision | Recall | F1 | ROC AUC | AP | FPR | FNR | Alert rate | TP/FP/TN/FN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 580 | 13 | 0.033 | 0.538 | 0.062 | 0.566 | 0.0271 | 0.36 | 0.462 | 0.3638 | 7/204/363/6 |
| mixed | 582 | 11 | 0.026 | 0.091 | 0.041 | 0.538 | 0.0435 | 0.065 | 0.909 | 0.0653 | 1/37/534/10 |
| brownfield | 575 | 11 | 0.041 | 0.182 | 0.067 | 0.534 | 0.03 | 0.083 | 0.818 | 0.0852 | 2/47/517/9 |

Average precision (AP) supplies the precision–recall summary. A constant-score classifier has AP equal to test prevalence and ROC AUC 0.5 when both classes are present. The never-alert rule has zero recall and zero workload. The always-alert rule has unit recall and precision equal to prevalence. Per-scenario baselines, class counts, validation load, thresholds, split times and feature importances are in [raw training results](evidence/scenarios/results.json).

## Independent synthetic run

The mixed forest, imputer and threshold trained at seed 42 were evaluated once on seed 137 after the method was fixed. Among 1,931 eligible vehicles it detected 2 defects, missed 36, and issued 155 false alerts. ROC AUC was 0.470, AP 0.0187, compared with prevalence 0.0197. Precision was 0.013, recall 0.053, F1 0.021, FPR 0.082, FNR 0.947 and alert load 0.081. The model did not outperform constant-score ranking on this independent run. A deployment claim is unsupported. [Independent results](evidence/independent-ml.json)

```sh
python scripts/validate_new_seed.py data/generated/my-experiment/mixed_1.db data/generated/independent-137.json --seed 137
```

The Isolation Forest fits per sensor profile with 200 trees on the earliest 60% of eligible visits. Its medians, MAD scaling, score rescaling and 99th percentile cutoff now use that prefix. Sparse/manual groups and groups under 200 rows are skipped. Scores still describe retrospective unusualness. No labeled anomaly ground truth or independent plant validation establishes detector accuracy. Whole-corpus dashboard trust metrics include fitted observations. They must not substitute for the held-out table. Environmental observations are shared at site level. Cross-factory transfer, calibration and real-time streaming prediction remain unvalidated.
