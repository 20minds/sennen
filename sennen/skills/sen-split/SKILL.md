---
name: sen-split
description: Check a split strategy for leakage and common pitfalls.
---

# Sennen `/sen-split`

Use this command when the user explicitly wants split design.

## Read First

- relevant source tables under `data/`
- existing split code under `src/data/`
- `config/metrics/metrics.yaml` if it exists

## Required Output

- `config/split/split.yaml`
- optional split code in `src/data/data_00x_split.py`
- optional split manifests under `data/splits/`

## Workflow

1. Inspect the dataset shape, identifiers, and time structure.
2. Choose the safest split strategy consistent with the task.
3. Test the current setup for leakage and common evaluation pitfalls.
4. Record exact leakage guards in `config/split/split.yaml`.
5. If executable split code is needed, create `src/data/data_001_split.py` or the next available numbered split file.
6. If split manifests are materialized and DVC is available, track them with DVC.

## Examples

- Git: commit split configuration, split scripts, and sampled ID manifests so reviews can inspect the logic.
- DVC: if split outputs are materialized under `data/splits/`, prefer tracking that directory with `uv run dvc add data/splits/`, then run `uv run dvc status` to confirm the split artifacts are tracked. If the repo intentionally treats all of `data/` as one DVC-managed artifact boundary, `uv run dvc add data/` is also acceptable.
- `uv`: prefer keeping split tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical checks: grouped patient splits for medical data, chronological splits for lab time series, scaffold splits for chemistry, and no shared assay/entity IDs across train and eval.

## Leakage Guards To Consider

- suspicious columns that directly encode the target
- post-outcome or future-only features
- train/test contamination in current code or saved artifacts
- no entity appears across train and validation/test
- no future records appear in earlier folds
- no preprocessing is fit outside the training partition
- no target-derived features are constructed before the split

## Rules

- Be specific about why the chosen split is safe.
- Own leakage and contamination checks in this skill.
- If there is ambiguity about entity or time columns, call it out instead of guessing quietly.
- If the repo already has mixed Git-tracked files and `.dvc` files inside `data/`, do not blindly replace that with `uv run dvc add data/`.
- Prefer sortable split scripts such as `src/data/data_001_split.py` and `src/data/data_002_grouped_split.py`.
- If extra Python packages are needed for split logic, install them instead of weakening the split checks.
- If the repo uses `uv`, add those packages with `uv add`.
- If split files are materialized under `data/splits/` and DVC is available, prefer explicit tracking with `uv run dvc add data/splits/` and verify with `uv run dvc status`.
