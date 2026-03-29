---
name: sennen
description: |
  ML research plugin for scientific datasets with Git and DVC-aware workflows. Use when
  working across 100+ scientific data sources and you need help with data access, leakage-safe
  splits, metrics, baselines, experiments, defects, or preprocessing.

  Suggest these sub-skills when relevant:
  - scientific data access and schema inspection -> /sen:data
  - data structure and distribution inspection -> /sen:visualize
  - dataset inspection and quality checks -> /sen:defects
  - evaluation metric selection -> /sen:metrics
  - leakage-safe validation design -> /sen:split
  - preprocessing design -> /sen:preprocess
  - simplest model to beat -> /sen:baseline
  - validation and failure analysis -> /sen:experiment
  - critique of the current ML plan -> /sen:review
  - model explanation and feature attribution -> /sen:explain
---

Use Sennen as a repo-native ML workflow plugin. Keep substantive artifacts in `data/`, `src/`, `reports/`, `models/`, and `config/`. Prefer explicit, reviewable outputs over hidden plugin state.

Repo contract:
- raw source data goes in `data/raw/`
- model-ready derived data goes in `data/processed/`
- materialized split artifacts go in `data/splits/`
- configs live under `config/`
- experiment code lives under `src/experiment/`
- reports live under `reports/`

Operational rules:
- respect existing Git and DVC structure when handling data and experiments
- if data is downloaded into `data/raw/` or materialized into `data/processed/` or `data/splits/`, track it with DVC when DVC is available
- prefer `uv run dvc add data/` only when `data/` is intentionally one DVC-managed artifact boundary; otherwise use narrower directories
- use MLflow for run tracking when the repo uses it or the user asks for tracked runs, and prefer `sqlite:///mlflow.db` over file-backed metadata stores
- if a Python package is needed, add it instead of removing the dependency from the approach
- if the repo uses `uv`, add project dependencies with `uv add` rather than `uv pip install` or ad hoc package managers
