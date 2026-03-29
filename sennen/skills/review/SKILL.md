---
name: sen:review
description: Review the current ML approach.
---

# Sennen `/review`

Use this skill to critique the current ML approach before investing further in implementation.

## Read First

- `config/metrics/metrics.yaml`
- `config/split/split.yaml`
- `config/preprocess/pipeline.yaml` if it exists
- `reports/experiments_latest.md` and prior review notes if they exist

## Required Output

- `reports/review/00x_*.md`

## Workflow

1. Read `config/metrics/metrics.yaml`, `config/split/split.yaml`, `config/preprocess/pipeline.yaml`, and `reports/experiments_latest.md` if they exist.
2. Inspect the current repo structure, modeling assumptions, and available results.
3. Review:
   - whether the task framing is coherent
   - whether the split and metric choices are appropriate
   - whether preprocessing or feature logic risks leakage
   - whether the baseline and experiment design are credible
   - whether experiment tracking is coherent across Git, DVC, and MLflow
   - whether the current approach is too complex or too weak
4. Write a concise critique with concrete risks, gaps, and next steps to `reports/review/001_initial_review.md` or the next available numbered review note.

## Examples

- Git: commit the review note so changes in scientific direction are visible in code review.
- DVC: if the review refers to large artifacts or result tables, keep those in DVC and reference them from `reports/review/`.
- Tracking: call out inconsistent run tracking, missing dataset/version references, weak MLflow hygiene, or continued use of deprecated file-backed MLflow metadata.
- `uv`: prefer keeping analysis and evaluation tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical review findings: wrong metric for class imbalance, random split where group leakage exists, unnecessary deep model before a tree baseline, or feature engineering that uses post-outcome signals.

## Rules

- Critique the approach, not just the code quality.
- Prefer concrete scientific and evaluation risks over generic advice.
- If evidence is missing, say what must be checked next.
- Prefer numbered review notes such as `reports/review/001_initial_review.md` and `reports/review/002_post_baseline_review.md`.
- If reproducing the current approach requires extra Python packages, install them instead of removing the dependency from the reproduction path.
- If the repo uses `uv`, add those packages with `uv add`.
