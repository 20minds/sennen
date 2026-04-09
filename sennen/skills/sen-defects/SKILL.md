---
name: sen-defects
description: Identify defects in the data itself.
---

# Sennen `/sen-defects`

Use this command when the user explicitly wants data quality interrogation.

## Read First

- source data under `data/`
- loading code under `src/data/`
- existing quality reports under `results/data_quality/`

## Required Output

- `results/data_quality/00x_*.md`
- optional validator or profiling code in `src/data/data_00x_*.py`

## Workflow

1. Inspect the dataset or data-loading code.
2. Write findings to `results/data_quality/001_profile.md` or the next available numbered report.
3. If reusable validation code is needed, create `src/data/data_001_validate.py` or the next available numbered file.

## Inspect For

- missing values and missingness patterns
- duplicate rows and duplicate entity identifiers
- impossible values, outliers, and bad types
- target imbalance and rare-category sparsity
- malformed records and broken joins
- inconsistent labels or suspicious label noise
- schema mismatches across files or sources

## Examples

- Git: commit data-profile findings and any validator scripts; do not commit raw defect dumps if they are large or sensitive.
- DVC: if defect reports are large tables or plots, prefer storing them under `results/data_quality/` with DVC tracking.
- `uv`: prefer keeping profiling and validation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical defects: duplicated patient visits, mislabeled microscopy classes, impossible negative counts, malformed timestamps, broken joins, or inconsistent schema between source files.

## Rules

- Prefer concrete examples from the dataset over generic warnings.
- Keep this skill focused on raw data quality and integrity.
- Leave leakage and contamination checks to `/sen-split`.
- If you cannot inspect the raw data, inspect the data-loading code and state the limitation.
- Prefer numbered reports such as `results/data_quality/001_profile.md` and `results/data_quality/002_missingness.md`.
- If extra Python validation packages are needed, install them instead of removing the validation step.
- If the repo uses `uv`, add those packages with `uv add`.
