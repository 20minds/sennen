---
name: sen:visualize
description: Inspect data structure and distributions.
---

# Sennen `/visualize`

Use this skill to inspect data before modeling or when debugging suspicious results.

## Read First

- source data under `data/`
- relevant quality notes under `reports/data_quality/`
- existing plots under `reports/figures/`

## Required Output

- `reports/figures/`
- optional plotting code in `src/visualize/00x_*.py`
- concise notes in `reports/figures/00x_*.md`

## Workflow

1. Read `reports/data_quality/` if it exists.
2. Inspect the dataset shape, column types, target distribution, and key feature distributions.
3. Identify what should be visualized to understand:
   - class imbalance
   - missingness
   - outliers
   - temporal drift
   - train/eval mismatch
   - suspicious feature-target relationships
4. Create or update reproducible plotting code in `src/visualize/001_inspect.py` or the next available numbered file.
5. Write concise visualization notes in `reports/figures/001_overview.md` or the next available numbered report.

## Examples

- Git: commit plotting code, notebooks, and compact visualization notes; avoid committing bulky rendered artifacts unless they are essential.
- DVC: store large plot collections, HTML reports, or generated figures under DVC when they are too large for Git.
- `uv`: prefer keeping plotting and notebook tooling in the repo's managed `uv` environment when the project already uses `uv`.
- Typical visuals: target histogram, class balance bar chart, missingness heatmap, numeric feature distributions, temporal drift plots, correlation heatmaps, and embedding projections for high-dimensional scientific data.

## Rules

- Prefer visuals that answer a modeling question, not generic dashboards.
- Call out plots that may reveal leakage or distribution shift.
- Keep notes concise and tied to downstream decisions.
- Prefer numbered visualization scripts such as `src/visualize/001_inspect.py` and `src/visualize/002_target_drift.py`.
- If extra Python plotting packages are needed, install them instead of dropping the visualization approach.
- If the repo uses `uv`, add those packages with `uv add`.
