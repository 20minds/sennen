#!/usr/bin/env python3
"""Initialize a repo-native scientific ML workspace for Sennen."""

from __future__ import annotations

from pathlib import Path


ROOT = Path.cwd()

DIRS = [
    ".sennen",
    "config",
    "config/metrics",
    "config/split",
    "config/preprocess",
    "config/experiment",
    "data/raw",
    "data/preprocessed",
    "data/processed",
    "models",
    "reports/data_quality",
    "reports/explanations",
    "reports/review",
    "reports/figures",
    "src/data",
    "src/preprocess",
    "src/experiment",
    "src/visualize",
]

FILES = {
    ".sennen/config.yaml": """layout_version: 1
task_type: unknown
target: null
dataset_paths:
  - data/raw
entity_id: null
time_column: null
group_column: null
notes: []
repo_layout:
  raw_data: data/raw
  preprocessed_data: data/preprocessed
  processed_data: data/processed
  preprocess_code: src/preprocess
  experiment_code: src/experiment
  visualize_code: src/visualize
  reports: reports
  config: config
""",
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
    "config/preprocess/pipeline.yaml": """imputation: []
encoding: []
scaling: []
feature_filters: []
target_transform: null
notes: []
""",
    "config/experiment/baseline.yaml": """name: baseline
entrypoint: src/experiment/001_baseline.py
metric_config: config/metrics/metrics.yaml
split_config: config/split/split.yaml
preprocess_config: config/preprocess/pipeline.yaml
notes: []
""",
    "reports/data_quality/001_profile.md": """# Data Profile

Run `/defects` to replace this stub with a real profile.
""",
    "reports/review/001_initial_review.md": """# Review

Run `/review` to replace this stub with a real critique.
""",
    "reports/experiments_latest.md": """# Experiment Report

Run `/experiment` to replace this stub with a real report.
""",
    "reports/explanations/001_initial_explanation.md": """# Explanation

Run `/sen:explain` to replace this stub with a real explanation report.
""",
    "reports/figures/README.md": """# Figures

Store generated plots and visualization outputs here. Use DVC if artifacts become large.
""",
    "src/data/001_ingest.py": '"""Data ingestion entrypoint."""\n',
    "src/preprocess/001_preprocess.py": '"""Preprocessing entrypoint."""\n',
    "src/experiment/001_baseline.py": '"""Baseline experiment entrypoint."""\n',
    "src/visualize/001_inspect.py": '"""Visualization entrypoint."""\n',
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
