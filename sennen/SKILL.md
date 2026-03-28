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

Use Sennen as a repo-native ML workflow plugin. Keep substantive artifacts in `data/`, `src/`, `reports/`, `models/`, and `config/`. Reserve `.sennen/config.yaml` for minimal plugin metadata only. Respect existing Git and DVC structure when handling data and experiments. If data is downloaded into `data/raw/` or generated into `data/processed/`, version it with DVC when DVC is available. For experiment tracking, use MLflow when the repo already uses it or when the user explicitly asks for run tracking, and prefer a local SQLite tracking URI such as `sqlite:///mlflow.db` over deprecated file-backed metadata stores. If a Python package is needed, add it instead of removing the dependency from the approach. If the repo uses `uv`, add project dependencies with `uv add` rather than `uv pip install` or ad hoc package managers.
