---
name: sen:experiment
description: Run and compare reproducible experiments with Git and DVC-aware outputs.
---

# Sennen `/experiment`

Use this skill to validate the current approach and compare experiment results.

## Read First

- `config/metrics/metrics.yaml`
- `config/split/split.yaml`
- `config/preprocess/pipeline.yaml` if it exists
- current experiment reports and existing code under `src/experiment/`

## Required Outputs

- experiment code in `src/experiment/00x_*.py`
- concise run summary in `reports/experiments_latest.md`
- optional model artifacts in `models/`

## Workflow

1. Read `config/metrics/metrics.yaml`, `config/split/split.yaml`, `config/preprocess/pipeline.yaml`, and current experiment reports if they exist.
2. Inspect current code, configs, and prior experiment outputs.
3. Check that the experiment respects the current split and metric contracts.
4. If the repo uses MLflow or the user asks for tracked runs, keep the new run compatible with the repo's MLflow setup and prefer `sqlite:///mlflow.db` for local metadata.
5. Compare outcomes against the baseline.
6. Create or update `src/experiment/001_baseline.py` or the next available numbered experiment file for the run being added.
7. Write a concise report with setup, results, regressions, and next ablations to `reports/experiments_latest.md`.

## Examples

- Git: commit experiment config changes separately from result updates when possible so code review stays readable.
- DVC: prefer versioned `reports/` artifacts and large outputs tracked with DVC when the repo already uses DVC.
- MLflow: if the repo uses MLflow or the user asks for tracked runs, log params, metrics, and model references consistently there, and prefer `sqlite:///mlflow.db` over file-backed metadata for local setups.
- `uv`: prefer keeping training and validation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical report contents: metric deltas versus baseline, ablation table, seed stability, failure slices, and whether the result is credible enough to merge.

## Rules

- Prefer reproducible configs and artifact paths over informal notes.
- If the repo already uses DVC, keep experiment artifacts compatible with it.
- If the repo already uses MLflow, keep new runs compatible with its tracking conventions.
- If the code is not runnable, report the gap instead of inventing results.
- Prefer numbered experiment scripts such as `src/experiment/001_baseline.py` and `src/experiment/002_xgboost.py`.
- If extra Python training or evaluation packages are needed, install them instead of simplifying the experiment only to avoid a dependency.
- If the repo uses `uv`, add those packages with `uv add`.
