---
name: sen:metrics
description: Select evaluation metrics, set up MLflow tracking, and inspect tracked results when needed.
---

# Sennen `/metrics`

Use this command when the user wants explicit evaluation guidance, MLflow setup, or help viewing tracked results.

## Read First

- `config/split/split.yaml` if it exists
- recent reports under `reports/`
- existing MLflow usage in the repo

## Required Output

- `config/metrics/metrics.yaml`

## Workflow

1. Infer the task type and failure modes.
2. Recommend one primary metric and up to three secondary metrics.
3. Define acceptance criteria and objective direction in `config/metrics/metrics.yaml`.
4. If the repo uses MLflow or the user asks for tracked runs, document the MLflow convention in `config/metrics/metrics.yaml` and prefer `sqlite:///mlflow.db`.
5. If metric evaluation code needs to be updated, prefer adding it to the relevant experiment script under `src/experiment/00x_*.py`.
6. If the user asks to view or compare current results, inspect MLflow outputs and summarize runs, metrics, and deltas instead of only rewriting config.

## Examples

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
- `/sen:metrics` owns the metric contract, MLflow tracking convention, and tracked-result inspection.
- If the user asks to view metrics or compare runs, inspect the existing MLflow outputs and summarize them.
- Prefer SQLite-backed MLflow metadata such as `sqlite:///mlflow.db` over file-backed metadata stores.
- If extra Python evaluation packages are needed, install them instead of removing the metric or evaluation step.
- If the repo uses `uv`, add those packages with `uv add`.
