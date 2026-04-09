---
name: sen-plan
description: Define the prediction task, evaluation contract, and leakage-aware plan before modeling.
---

# Sennen `/sen-plan`

Use this skill when the user wants to frame an ML problem before serious modeling starts.

## Read First

- repo readiness from the `sen-doctor` skill
- available source data under `data/`
- existing planning notes under `results/review/`
- current split and metric config under `config/` if they exist

## Required Outputs

- `config/split/split.yaml`
- `config/metrics/metrics.yaml`
- a concise planning note in `results/review/001_plan.md` or the next available numbered review note

## Maps To

- `sen-doctor`
- `sen-defects`
- `sen-split`
- `sen-metrics`
- optionally `sen-visualize`

## Workflow

1. Check whether the repo is ready for the Sennen workflow. If core repo scaffolding, config paths, or DVC/MLflow conventions are missing, use the `sen-doctor` skill first.
2. Clarify the target, unit of prediction, time horizon, and intended use.
3. Identify obvious data-quality risks that could change the problem framing.
4. Define a leakage-safe split strategy and explicit leakage guards.
5. Define the metric contract: primary metric, supporting metrics, objective direction, and acceptance criteria.
6. Add lightweight visualization only when it helps clarify the target, imbalance, drift, or split assumptions.
7. Write a concise planning note that states:
   - what is being predicted
   - what data is in scope
   - how success will be measured
   - what could invalidate the result
   - what baseline should be expected next

## Examples

- Doctor mapping: if the repo is missing `config/`, `results/`, or expected ML workflow structure, use the `sen-doctor` skill first instead of writing planning artifacts into an incomplete repo.
- Planning note: write a short contract such as “predict month-12 enrollment-open status from information available at trial launch, evaluated with AUROC, AUPRC, and calibration under an unseen-sponsor holdout.”
- Split mapping: use the `sen-split` skill to define time- or group-aware evaluation before any modeling code is added.
- Metrics mapping: use the `sen-metrics` skill to make the primary metric explicit before experimentation starts.
- Defect mapping: use the `sen-defects` skill to surface missing labels, duplicated entities, malformed dates, or schema mismatches that affect the plan.

## Rules

- `/sen-plan` owns problem framing and evaluation design, not model training.
- `/sen-plan` should rely on the `sen-doctor` skill when repo readiness is missing, instead of assuming the repo is already prepared.
- Do not silently invent target semantics when the problem statement is ambiguous; call out the ambiguity in the plan note.
- Prefer a short, explicit contract over a long generic writeup.
- If data access is still unresolved, route to `/sen-data` or the relevant `db-*` skill before pretending the plan is settled.
- If extra Python packages are needed for planning or lightweight inspection, install them instead of weakening the workflow.
- If the repo uses `uv`, add those packages with `uv add`.
