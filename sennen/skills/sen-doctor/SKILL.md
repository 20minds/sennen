---
name: sen-doctor
description: Diagnose and repair repo readiness for the Sennen workflow.
---

# Sennen `/sen-doctor`

Use this skill when the repo needs to be checked and repaired before planning, baselines, or experiments begin.

## Read First

- current repo structure
- existing `pyproject.toml`, `.gitignore`, DVC files, and MLflow usage
- existing `config/`, `data/`, `results/`, and `src/` layout if present

## Required Outputs

- a repo-ready directory and config scaffold under `config/`, `data/`, `results/`, `models/`, and `src/`
- a concise readiness note in `results/review/000_repo_init.md`

## Bundled Initializer

A bundled script can scaffold the full repo layout in one step:

- plugin mode: `plugins/sennen/scripts/init_project.py`
- source repo: `sennen/scripts/init_project.py`

Run it from the repo root with `python3 <path>/init_project.py` or `uv run python <path>/init_project.py`. It creates all standard directories and non-destructively writes starter config and stub files. Prefer it over manually creating the scaffold when the script is available; fall back to creating files with tools when it is not.

## Workflow

1. Check whether the repo already has Git, `pyproject.toml`, `uv`, DVC, and MLflow conventions in place.
2. Create missing repo-native folders needed by the Sennen workflow:
   - `config/`
   - `data/raw/`
   - `data/processed/`
   - `data/splits/`
   - `models/`
   - `results/`
   - `src/`
3. Create missing starter files only where they help establish the workflow:
   - `config/metrics/metrics.yaml`
   - `config/split/split.yaml`
   - `config/prepare/pipeline.yaml`
   - `results/review/000_repo_init.md`
4. Validate whether DVC and MLflow are configured coherently for the repo.
5. Document what was found, what was created, and what is still missing before `/sen-plan` or `/sen-experiment` should proceed.

## Examples

- Repo readiness: confirm that the repo has a `pyproject.toml`, sane `.gitignore`, and the expected top-level folders before modeling starts.
- DVC readiness: note whether DVC is installed and initialized, and whether data should be tracked at `data/` or narrower boundaries.
- MLflow readiness: note whether MLflow is available and whether local tracking should use `sqlite:///mlflow.db`.
- Workflow handoff: if the repo is ready, point the user to `/sen-plan`; if not, say exactly what still blocks reliable ML work.

## Rules

- `/sen-doctor` diagnoses and repairs repo readiness; it does not define the prediction task or train models.
- Prefer creating the minimum viable scaffold over generating a large amount of boilerplate.
- Respect existing structure and do not overwrite established project conventions casually.
- Distinguish clearly between host/plugin installation and repo diagnosis:
  - `./setup` installs the plugin and host wiring
  - `/sen-doctor` prepares and validates the ML repo itself
- If extra Python packages are needed for repo validation or readiness checks, install them instead of weakening the workflow.
- If the repo uses `uv`, add those packages with `uv add`.
