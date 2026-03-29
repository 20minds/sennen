---
name: sen:baseline
description: Establish a reproducible baseline to beat.
---

# Sennen `/baseline`

Use this skill after metrics and split assumptions exist. The goal is to create a baseline that is honest, reproducible, and hard to fool yourself against.

## Read First

- `config/metrics/metrics.yaml`
- `config/split/split.yaml`
- existing experiment code under `src/experiment/`

## Required Outputs

- one baseline implementation in `src/experiment/00x_baseline.py`
- a short rationale in `reports/experiments_latest.md` or `reports/review/`
- optional baseline artifacts in `models/`

## Workflow

1. Read `config/metrics/metrics.yaml` and `config/split/split.yaml`.
2. Inspect the data modality and existing project code.
3. Choose the simplest defensible baseline:
   - majority class or mean predictor if that is still informative
   - regularized linear model for sparse or interpretable tabular tasks
   - tree ensemble baseline for mixed tabular features
4. Implement the baseline in `src/experiment/001_baseline.py` or the next available numbered experiment file.
5. Record:
   - what baseline was chosen
   - why it is appropriate
   - what metric it optimizes
   - what result future models must exceed

## Examples

- Git: commit the baseline code and config together so the baseline is reviewable.
- DVC: if the baseline writes large model artifacts or prediction tables, prefer `models/` or `reports/` artifacts tracked with DVC instead of Git-tracked blobs.
- Tracking: use MLflow for baseline metrics and params when the repo already uses it or the user explicitly asks for tracked runs, and prefer `sqlite:///mlflow.db` for local metadata.
- `uv`: prefer keeping baseline tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical baselines: majority class, mean regressor, logistic regression, elastic net, random forest, or a small gradient-boosted tree model with minimal tuning.

## Rules

- Prefer clarity over leaderboard chasing.
- Do not silently upgrade the baseline into a tuned production model.
- If the repo has no ML stack yet, create a minimal script instead of introducing a large framework.
- Respect existing Git and DVC conventions for outputs and artifacts.
- Keep baseline metrics compatible with the repo's MLflow setup when MLflow is used.
- Prefer numbered experiment scripts such as `src/experiment/001_baseline.py`.
- If extra Python modeling packages are needed, install them instead of changing the baseline just to avoid a dependency.
- If the repo uses `uv`, add those packages with `uv add`.
