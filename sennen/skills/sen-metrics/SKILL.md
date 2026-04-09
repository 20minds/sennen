---
name: sen-metrics
description: Select evaluation metrics, set up MLflow tracking, and inspect tracked results when needed.
---

# Sennen `/sen-metrics`

Use this command when the user wants explicit evaluation guidance, MLflow setup, or help viewing tracked results.

## Read First

- `config/split/split.yaml` if it exists
- recent experiment summaries under `results/exp_00x_<label>/`
- existing MLflow usage in the repo

## Required Output

- `config/metrics/metrics.yaml`

## Workflow

1. Infer the task type and failure modes.
2. Recommend one primary metric and up to three secondary metrics.
3. Define acceptance criteria and objective direction in `config/metrics/metrics.yaml`.
4. If the repo uses MLflow or the user asks for tracked runs, document the MLflow convention in `config/metrics/metrics.yaml` and prefer `sqlite:///mlflow.db`.
5. If metric evaluation code needs to be added or updated, prefer shared evaluation code under `src/lib/` or another reusable module rather than duplicating metric logic in each experiment script.
6. Prefer metrics computed from persisted experiment artifacts such as `data/results/exp_00x/predictions.parquet`, `data/results/exp_00x/predictions.csv`, or similar run-local outputs instead of only transient in-memory objects.
7. Prefer lightweight metric summaries and run metadata in `results/exp_00x_<label>/metrics.yaml` or adjacent files so they stay easy to inspect in Git.
8. Encourage each experiment to record `runtime_seconds` in `results/exp_00x_<label>/metrics.yaml` so metric comparisons can include compute cost as well as model quality.
9. If the user asks to view or compare current results, inspect MLflow outputs, `results/exp_00x_<label>/metrics.yaml`, and related experiment result artifacts, then summarize runs, metrics, deltas, and runtime tradeoffs instead of only rewriting config.

## Examples

- Git: commit `config/metrics/metrics.yaml` so metric changes are reviewed explicitly.
- MLflow: when the repo already uses MLflow or the user explicitly asks for it, keep metrics compatible with the existing MLflow setup, prefer `sqlite:///mlflow.db` for local metadata, and inspect tracked runs there when the user wants to compare results.
- MLflow UI: if `mlflow ui` fails with `Operation not permitted` in a sandboxed environment, rerun it outside the sandbox so it can bind the local port.
- DVC: keep large evaluation artifacts compatible with DVC, especially machine-readable prediction tables under `data/results/exp_00x/`.
- `uv`: prefer keeping evaluation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Shared evaluation: prefer reusable helpers in `src/lib/` such as prediction loading, metric computation, calibration evaluation, and threshold sweeps instead of rewriting them inside every experiment entrypoint.
- Artifact-first evaluation: a strong default is to persist predictions in `data/results/exp_00x/` and compute metrics from those persisted predictions so results can be recomputed and audited later.
- Git-friendly summaries: keep small summaries such as `results/exp_00x_<label>/metrics.yaml` in Git-friendly locations instead of hiding them inside large DVC-managed directories.
- Runtime tracking: include `runtime_seconds` in `results/exp_00x_<label>/metrics.yaml` so speed/compute tradeoffs are visible during comparison.
- Typical choices: AUROC and AUPRC for imbalanced classification, macro F1 for multi-class fairness concerns, concordance index for survival settings, RMSE or MAE for regression, and calibration error when decision thresholds matter.

## Rules

- Avoid defaulting to accuracy for imbalanced classification.
- Prefer metrics that reflect the deployment or research decision boundary.
- Explain when calibration metrics or ranking metrics matter.
- `/sen-metrics` owns the metric contract, MLflow tracking convention, and tracked-result inspection.
- If the user asks to view metrics or compare runs, inspect the existing MLflow outputs and summarize them.
- Prefer shared metric computation code over per-experiment duplication.
- Prefer computing metrics from persisted experiment outputs when the repo stores predictions or evaluation tables.
- Prefer large prediction artifacts under `data/results/exp_00x/` and small summaries under `results/exp_00x_<label>/`.
- Prefer recording `runtime_seconds` in `results/exp_00x_<label>/metrics.yaml` so experiment quality can be interpreted alongside cost.
- Prefer SQLite-backed MLflow metadata such as `sqlite:///mlflow.db` over file-backed metadata stores.
- If extra Python evaluation packages are needed, install them instead of removing the metric or evaluation step.
- If the repo uses `uv`, add those packages with `uv add`.
