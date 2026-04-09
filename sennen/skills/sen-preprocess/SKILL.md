---
name: sen-preprocess
description: Fix data defects and engineer features in a reproducible preprocessing pipeline.
---

# Sennen `/sen-preprocess`

Use this skill when the user wants preprocessing design or feature engineering.

## Read First

- `config/split/split.yaml`
- current preparation code under `src/prepare/`
- current raw and processed data layout under `data/`

## Required Output

- `config/prepare/pipeline.yaml`
- preparation code in `src/prepare/prep_00x_*.py`
- outputs in `data/processed/`

## Include

- imputation rules
- categorical encoding strategy
- numeric scaling decisions
- feature exclusion rules
- target transforms if needed
- notes about fit-on-train-only requirements

## Workflow

1. Read `config/split/split.yaml` and current preprocessing config if they exist.
2. Write or update `config/prepare/pipeline.yaml`.
3. Create or update `src/prepare/prep_001_pipeline.py` or the next available numbered preparation file.
4. Write derived outputs to `data/processed/`.
5. If processed outputs were materialized and DVC is available, track them with DVC.

## Examples

- Git: commit preprocessing specs, transformer code, and feature lists so changes are diffable.
- DVC: if preprocessing produces cached features, prefer `data/processed/` tracked with DVC instead of Git. In clean repos where `data/` is one DVC-managed artifact boundary, prefer `uv run dvc add data/`, then run `uv run dvc status`. If `data/` already mixes Git-tracked metadata with DVC artifacts, prefer `uv run dvc add data/processed/`.
- `uv`: prefer keeping preprocessing and feature-generation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical fixes: median imputation, one-hot or target-safe categorical encoding, log transforms for skewed lab values, dropping leakage columns, and domain-derived aggregate features.

## Rules

- Tie preprocessing decisions to the current split plan.
- Keep the plan implementable in ordinary Python ML code.
- Avoid transformations that require future information unless the split plan explicitly supports them.
- Respect existing Git and DVC conventions for derived data and feature artifacts.
- Prefer sortable scripts such as `src/prepare/prep_001_pipeline.py` and `src/prepare/prep_002_initial_cleaning.py`.
- If extra Python preprocessing packages are needed, install them instead of dropping the preprocessing step.
- If the repo uses `uv`, add those packages with `uv add`.
- When outputs are written to `data/processed/` and DVC is available, track them with DVC rather than leaving them unmanaged. Prefer `uv run dvc add data/` when `data/` is the intended artifact boundary; otherwise prefer `uv run dvc add data/processed/`. Verify with `uv run dvc status`.
