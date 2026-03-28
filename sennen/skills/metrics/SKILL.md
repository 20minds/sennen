---
name: sen:metrics
description: Select evaluation metrics, set up MLflow tracking, and inspect tracked results when needed.
---

# Sennen `/metrics`

Use this command when the user wants explicit evaluation guidance, MLflow setup, or help viewing tracked results.

## Required Output

- `config/metrics/metrics.yaml`

## Workflow

1. Read `.sennen/config.yaml` and `reports/data_quality/` if present.
2. Infer the task type and failure modes.
3. Recommend one primary metric and up to three secondary metrics.
4. Decide whether MLflow should be used for tracked experiment metrics.
5. If MLflow is used, prefer a local SQLite tracking URI such as `sqlite:///mlflow.db` over file-backed metadata stores.
6. Document acceptance criteria, objective direction, and MLflow usage in `config/metrics/metrics.yaml`.
7. If metric evaluation code needs to be updated, prefer adding it to the relevant experiment script under `src/experiment/00x_*.py`.
8. If the user asks to view or compare current results, inspect the active backend and summarize the tracked runs, metrics, and deltas instead of only rewriting config.

## Concrete Examples

- Git: commit `config/metrics/metrics.yaml` so metric changes are reviewed explicitly.
- MLflow: when the repo already uses MLflow or the user explicitly asks for it, keep metrics compatible with the existing MLflow setup, prefer `sqlite:///mlflow.db` for local metadata, and inspect tracked runs there when the user wants to compare results.
- MLflow UI: if `mlflow ui` fails with `Operation not permitted` in a sandboxed environment, rerun it outside the sandbox so it can bind the local port.
- DVC: keep large evaluation artifacts and generated reports compatible with DVC.
- `uv`: prefer keeping evaluation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical choices: AUROC and AUPRC for imbalanced classification, macro F1 for multi-class fairness concerns, concordance index for survival settings, RMSE or MAE for regression, and calibration error when decision thresholds matter.

## Rules

- Avoid defaulting to accuracy for imbalanced classification.
- Prefer metrics that reflect the deployment or research decision boundary.
- Explain when calibration metrics or ranking metrics matter.
- `/sen:metrics` owns MLflow setup guidance and tracked-result inspection.
- If the user asks to view metrics or compare runs, inspect the existing MLflow outputs and summarize them.
- Prefer SQLite-backed MLflow metadata such as `sqlite:///mlflow.db` over file-backed metadata stores.
- If extra Python evaluation packages are needed, install them instead of removing the metric or evaluation step.
- If the repo uses `uv`, add those packages with `uv add`.
