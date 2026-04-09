#!/usr/bin/env python3
"""Initialize a repo-native scientific ML workspace for Sennen."""

from __future__ import annotations

from pathlib import Path


ROOT = Path.cwd()

DIRS = [
    "config",
    "config/metrics",
    "config/split",
    "config/prepare",
    "config/exp",
    "data/raw",
    "data/processed",
    "data/results",
    "data/splits",
    "models",
    "models/checkpoints",
    "models/exports",
    "results",
    "results/exp_001_baseline",
    "results/data_quality",
    "results/explanations",
    "results/review",
    "results/figures",
    "src/data",
    "src/prepare",
    "src/exp",
    "src/lib",
    "src/visualize",
]

FILES = {
    "config/metrics/metrics.yaml": """primary_metric: null
secondary_metrics: []
objective_direction: maximize
acceptance_criteria: []
notes: []
""",
    "config/split/split.yaml": """strategy: null
train_fraction: 0.7
validation_fraction: 0.15
test_fraction: 0.15
group_column: null
time_column: null
leakage_guards: []
notes: []
""",
    "config/prepare/pipeline.yaml": """imputation: []
encoding: []
scaling: []
feature_filters: []
target_transform: null
notes: []
""",
    "config/exp/exp_001_baseline.yaml": """id: experiment_001
kind: baseline
name: baseline
model_family: unspecified
status: planned
reference_role: primary
implementation:
  entrypoint: src/exp/exp_001_baseline.py
  data_results_dir: data/results/exp_001_baseline
  summary_dir: results/exp_001_baseline
metric_config: config/metrics/metrics.yaml
split_config: config/split/split.yaml
prepare_config: config/prepare/pipeline.yaml
comparison:
  compare_against: []
notes: []
""",
    "config/exp/tracking.yaml": """backend: mlflow
tracking_uri: sqlite:///mlflow.db
notes: []
""",
    "config/exp/remix.yaml": """policy:
  selector: uct
  objective_direction: maximize
  exploration_constant: 1.2
  secondary_pool: completed_any
  random_seed: 42
  concurrency_target: 2
state:
  total_visits: 0
  nodes: {}
history: []
""",
    "results/data_quality/001_profile.md": """# Data Profile

Run `/sen-defects` to replace this stub with a real profile.
""",
    "results/review/001_plan.md": """# Plan

Run `/sen-plan` to replace this stub with a real problem and evaluation plan.
""",
    "results/review/001_initial_review.md": """# Review

Run `/sen-review` to replace this stub with a real critique.
""",
    "results/exp_001_baseline/summary.md": """# Experiment Report

Run `/sen-experiment` to replace this stub with a real report.
""",
    "results/exp_001_baseline/metrics.yaml": """primary_metric: null
runtime_seconds: null
notes: []
""",
    "results/explanations/001_initial_explanation.md": """# Explanation

Run `/sen-explain` to replace this stub with a real explanation report.
""",
    "results/figures/001_overview.md": """# Figures

Store generated plots and visualization outputs here. Use DVC if artifacts become large.
""",
    "src/data/data_001_ingest.py": '"""Data ingestion entrypoint."""\n',
    "src/prepare/prep_001_pipeline.py": '"""Preparation entrypoint."""\n',
    "src/exp/exp_001_baseline.py": '"""Baseline experiment entrypoint."""\n',
    "src/lib/__init__.py": '"""Shared utilities for Sennen-driven ML projects."""\n',
    "src/visualize/vis_001_inspect.py": '"""Visualization entrypoint."""\n',
}


def main() -> None:
    for relative_path in DIRS:
        (ROOT / relative_path).mkdir(parents=True, exist_ok=True)
    for relative_path, content in FILES.items():
        destination = ROOT / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.write_text(content)
    print(f"Initialized repo-native Sennen layout in {ROOT}")


if __name__ == "__main__":
    main()
