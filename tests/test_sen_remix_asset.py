from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


ASSET = (
    Path(__file__).resolve().parents[1]
    / "sennen"
    / "skills"
    / "sen-remix"
    / "assets"
    / "uct.py"
)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False))


def test_select_with_uct_reads_outputs_and_prefers_best_discovered(tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "exp"

    _write_yaml(
        config_dir / "001_baseline.yaml",
        {
            "id": "experiment_001",
            "kind": "baseline",
            "implementation": {"summary_dir": "results/exp_001_baseline"},
        },
    )
    _write_yaml(
        config_dir / "014_candidate.yaml",
        {
            "id": "experiment_014",
            "kind": "discovered",
            "origin": "uct",
            "implementation": {"summary_dir": "results/exp_014_candidate"},
        },
    )
    _write_yaml(
        config_dir / "015_candidate.yaml",
        {
            "id": "experiment_015",
            "kind": "discovered",
            "origin": "uct",
            "implementation": {"summary_dir": "results/exp_015_candidate"},
        },
    )
    _write_yaml(
        tmp_path / "results" / "exp_001_baseline" / "metrics.yaml",
        {"status": "completed", "primary_metric": {"name": "roc_auc", "value": 0.80}},
    )
    _write_yaml(
        tmp_path / "results" / "exp_014_candidate" / "metrics.yaml",
        {"status": "completed", "primary_metric": {"name": "roc_auc", "value": 0.91}},
    )
    _write_yaml(
        tmp_path / "results" / "exp_015_candidate" / "metrics.yaml",
        {"status": "completed", "primary_metric": {"name": "roc_auc", "value": 0.84}},
    )
    _write_yaml(
        config_dir / "remix.yaml",
        {
            "policy": {
                "selector": "uct",
                "objective_direction": "maximize",
                "exploration_constant": 1.2,
                "random_seed": 7,
                "discovered_filter": {"require_origin": "uct"},
            },
            "state": {
                "total_visits": 10,
                "nodes": {
                    "experiment_014": {"visits": 3, "prior": 0.5},
                    "experiment_015": {"visits": 3, "prior": 0.1},
                },
            },
        },
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ASSET),
            "--config-dir",
            str(config_dir),
            "--remix-config",
            str(config_dir / "remix.yaml"),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["discovered_parent"] == "experiment_014"
    assert payload["diagnostics"]["experiment_014"]["metric_value"] == 0.91


def test_select_with_uct_ignores_incomplete_discovered_candidates(tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "exp"

    _write_yaml(
        config_dir / "001_baseline.yaml",
        {
            "id": "experiment_001",
            "kind": "baseline",
            "implementation": {"summary_dir": "results/exp_001_baseline"},
        },
    )
    _write_yaml(
        config_dir / "020_candidate.yaml",
        {
            "id": "experiment_020",
            "kind": "discovered",
            "origin": "uct",
            "implementation": {"summary_dir": "results/exp_020_candidate"},
        },
    )
    _write_yaml(
        config_dir / "021_candidate.yaml",
        {
            "id": "experiment_021",
            "kind": "discovered",
            "origin": "uct",
            "implementation": {"summary_dir": "results/exp_021_candidate"},
        },
    )
    _write_yaml(
        tmp_path / "results" / "exp_001_baseline" / "metrics.yaml",
        {"status": "completed", "primary_metric": {"name": "roc_auc", "value": 0.78}},
    )
    _write_yaml(
        tmp_path / "results" / "exp_020_candidate" / "metrics.yaml",
        {"status": "failed", "primary_metric": {"name": "roc_auc", "value": 0.99}},
    )
    _write_yaml(
        tmp_path / "results" / "exp_021_candidate" / "metrics.yaml",
        {"status": "completed", "primary_metric": {"name": "roc_auc", "value": 0.81}},
    )
    _write_yaml(
        config_dir / "remix.yaml",
        {
            "policy": {
                "selector": "uct",
                "discovered_filter": {"require_origin": "uct"},
            },
            "state": {"nodes": {}},
        },
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ASSET),
            "--config-dir",
            str(config_dir),
            "--remix-config",
            str(config_dir / "remix.yaml"),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["discovered_parent"] == "experiment_021"
