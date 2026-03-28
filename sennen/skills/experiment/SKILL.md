---
name: sen:experiment
description: Run and compare reproducible experiments with Git and DVC-aware outputs.
---

# Sennen `/experiment`

Use this skill to validate the current approach and compare experiment results.

## Goals

- run or inspect reproducible experiments
- compare against the current baseline
- record results in a Git and DVC-friendly way
- write `reports/experiments_latest.md`
- use MLflow consistently when tracked runs are needed

## Workflow

1. Read `config/metrics/metrics.yaml`, `config/split/split.yaml`, `config/preprocess/pipeline.yaml`, and current experiment reports if they exist.
2. Inspect current code, configs, and prior experiment outputs.
3. Check that the experiment respects the current split and metric contracts.
4. Decide whether MLflow should be used for this repo's tracked runs and prefer `sqlite:///mlflow.db` for local metadata when MLflow is enabled.
5. Compare outcomes against the baseline.
6. Create or update `src/experiment/001_baseline.py` or the next available numbered experiment file for the run being added.
7. Write a concise report with setup, results, regressions, and next ablations to `reports/experiments_latest.md`.

## Concrete Examples

- Git: commit experiment config changes separately from result updates when possible so code review stays readable.
- DVC: prefer versioned `reports/` artifacts and large outputs tracked with DVC when the repo already uses DVC.
- MLflow: use MLflow when the repo already uses it or when a richer run-comparison UI or remote tracking server is explicitly needed, and prefer `sqlite:///mlflow.db` over file-backed metadata for local setups.
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
