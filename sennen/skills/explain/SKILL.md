---
name: sen:explain
description: Explain model behavior with feature importance and SHAP when appropriate.
---

# Sennen `/sen:explain`

Use this skill to explain model behavior after a baseline or experiment has produced a credible model or set of predictions.

## Read First

- `config/metrics/metrics.yaml` if it exists
- current experiment outputs and saved model artifacts
- existing explanation notes under `reports/explanations/`

## Required Output

- explanation notes under `reports/explanations/00x_*.md`
- optional explanation code in `src/visualize/00x_explain.py`

## Workflow

1. Read `config/metrics/metrics.yaml`, current experiment outputs, and any saved model artifacts if they exist.
2. Identify the model family and what explanation methods are appropriate.
3. Prefer the simplest correct explanation technique:
   - built-in coefficients or importances when they are reliable enough
   - permutation importance when model-agnostic comparison is sufficient
   - SHAP values when local or global contribution analysis is needed and the model/data size makes it practical
4. Create or update `src/visualize/001_explain.py` or the next available numbered explanation file when executable analysis is needed.
5. Write explanation notes to `reports/explanations/001_initial_explanation.md` or the next available numbered report.

## Examples

- Git: commit explanation code and markdown summaries so interpretation changes are reviewable.
- DVC: if explanation outputs include large plots, SHAP arrays, or HTML reports, track them with DVC under `reports/explanations/` or `reports/figures/`.
- MLflow: if the explanation corresponds to a tracked run, reference the MLflow run or model version in the explanation note.
- `uv`: if explanation packages are needed, add them instead of dropping the explanation step. If the repo uses `uv`, add those packages with `uv add`.
- Typical outputs: ranked feature importance table, SHAP summary plot, SHAP dependence plots, per-example explanation notes, or coefficient tables for linear models.

## Rules

- Use SHAP when it is appropriate, not by default in every case.
- Prefer model-native or simpler explanations when they are sufficient and more stable.
- Call out explanation caveats, especially for correlated features, leakage-prone features, and unstable importances.
- If the current model is not credible yet, say so and defer detailed explanation until after the evaluation setup is trustworthy.
