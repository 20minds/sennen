---
name: sen-experiment
description: Run and compare reproducible experiments with Git and DVC-aware outputs.
---

# Sennen `/sen-experiment`

Use this skill to run the next experiment in the repo. If no completed experiment exists yet, start with a credible baseline. Otherwise, run a comparative experiment against the existing baseline and prior results.

## Read First

- `config/metrics/metrics.yaml`
- `config/split/split.yaml`
- `config/prepare/pipeline.yaml` if it exists
- `config/exp/*.yaml` if they exist
- current experiment results and existing code under `src/exp/`

## Required Outputs

- experiment code in `src/exp/exp_00x_<label>.py`
- large prediction and evaluation artifacts in `data/results/exp_00x/`
- machine-readable summary in `results/exp_00x_<label>/metrics.yaml`
- concise run summary in `results/exp_00x_<label>/summary.md`
- optional model artifacts in `models/`

## Workflow

1. Read `config/metrics/metrics.yaml`, `config/split/split.yaml`, `config/prepare/pipeline.yaml`, `config/exp/*.yaml` if they exist, and current experiment results.
2. Inspect current code, configs, and prior experiment outputs.
3. Determine whether the repo already has a completed experiment:
   - if not, run in baseline mode and create the first credible model to beat
   - if yes, run in comparative mode and create the next experiment against the existing baseline and prior results
4. If multiple baseline configs exist, use the one marked `reference_role: primary` as the default comparison anchor. If none is marked and multiple baselines exist, report the ambiguity instead of guessing silently.
5. Check that the experiment respects the current split and metric contracts.
6. If preprocessing materialized model-ready features, prefer consuming them from `data/processed/` rather than rebuilding hidden transformations inside the experiment.
7. If the repo uses MLflow or the user asks for tracked runs, keep the new run compatible with the repo's MLflow setup and prefer `sqlite:///mlflow.db` for local metadata.
8. In baseline mode, choose the simplest defensible baseline:
   - majority class or mean predictor if still informative
   - regularized linear model for sparse or interpretable tabular tasks
   - tree ensemble baseline for mixed tabular features
9. In baseline mode, create the first experiment config as a normal per-experiment YAML such as `config/exp/exp_001_baseline.yaml` with:
   - `kind: baseline`
   - `reference_role: primary`
   - an `implementation.entrypoint`
   - an `implementation.summary_dir`
10. Create or update `src/exp/exp_001_baseline.py` when bootstrapping the first run, or the next available labeled experiment file for later runs.
11. Write large machine-readable prediction and evaluation artifacts to `data/results/exp_00x/`, for example:
   - `predictions.parquet` or `predictions.csv`
   - optional per-slice or threshold analysis tables
12. Keep Git-friendly summaries in `results/exp_00x_<label>/`, especially a machine-readable `results/exp_00x_<label>/metrics.yaml` and a concise narrative `results/exp_00x_<label>/summary.md`.
13. Record `runtime_seconds` in `results/exp_00x_<label>/metrics.yaml` alongside the main evaluation metrics.
14. Compute the reported metrics from persisted experiment outputs when practical rather than only from transient in-memory values.
15. If result artifacts are large or already versioned with DVC conventions, keep `data/results/exp_00x/` compatible with DVC and track it when appropriate.
16. Write a concise report with setup, actual observed results, regressions, runtime tradeoffs, and next ablations to `results/exp_001_baseline/summary.md` or the next available labeled report, and keep the machine-readable summary in the matching `metrics.yaml`.

## Examples

- Git: commit experiment config changes separately from result updates when possible so code review stays readable.
- DVC: prefer large machine-readable outputs tracked with DVC when the repo already uses DVC, while keeping small Markdown and YAML summaries in `results/exp_00x_<label>/`.
- MLflow: if the repo uses MLflow or the user asks for tracked runs, log params, metrics, and model references consistently there, and prefer `sqlite:///mlflow.db` over file-backed metadata for local setups.
- `uv`: prefer keeping training and validation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Baseline mode: prefer clarity over cleverness and establish the first honest benchmark to beat.
- Processed data: if the repo materializes stable model-ready features in `data/processed/`, prefer consuming those artifacts directly instead of rebuilding preprocessing inside each experiment script.
- Prediction artifacts: a good default is to persist large prediction tables and related machine-readable outputs in `data/results/exp_00x/`.
- Lightweight summaries: keep `results/exp_00x_<label>/metrics.yaml` and similar small run metadata in Git-friendly files outside the larger result artifacts.
- Runtime metadata: include `runtime_seconds` in `results/exp_00x_<label>/metrics.yaml` by default.
- Typical report contents: metric deltas versus baseline, ablation table, seed stability, failure slices, and whether the result is credible enough to merge.

## Rules

- Prefer reproducible configs and artifact paths over informal notes.
- If the repo already uses DVC, keep experiment artifacts compatible with it.
- If the repo already uses MLflow, keep new runs compatible with its tracking conventions.
- If the code is not runnable, report the gap instead of inventing results.
- If no completed experiment exists yet, start in baseline mode instead of skipping directly to a more complex model.
- In baseline mode, prefer the simplest credible model over a tuned or high-complexity approach.
- Do not rely on a singleton baseline config; treat baselines as ordinary experiment configs under `config/exp/` with `kind: baseline`.
- If multiple baselines exist, use `reference_role: primary` to identify the default comparison baseline.
- Prefer reading model-ready features from `data/processed/` when that repo contract already exists.
- Prefer writing large prediction artifacts to `data/results/exp_00x/` and Git-friendly summaries such as `summary.md` and `metrics.yaml` to `results/exp_00x_<label>/`.
- Prefer computing reported metrics from persisted prediction artifacts and storing the resulting summary in `results/exp_00x_<label>/metrics.yaml`.
- Prefer storing experiment duration in `results/exp_00x_<label>/metrics.yaml` so later comparisons can include runtime cost.
- Prefer labeled experiment scripts such as `src/exp/exp_001_baseline.py` and `src/exp/exp_002_xgboost.py`.
- If extra Python training or evaluation packages are needed, install them instead of simplifying the experiment only to avoid a dependency.
- If the repo uses `uv`, add those packages with `uv add`.
