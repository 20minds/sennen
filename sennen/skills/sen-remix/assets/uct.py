#!/usr/bin/env python3
"""Select a primary remix parent from repo-local experiment metadata.

This asset reads experiment configs from ``config/exp/*.yaml``,
realized metrics from ``results/exp_00x_<label>/metrics.yaml``, and mutable
selection state from ``config/exp/remix.yaml``. It then computes a
UCT score for discovered experiments and selects:

- one discovered experiment using UCT

The result is printed as JSON for the calling skill to consume. The skill
itself is responsible for choosing any secondary parent with
``random.randint``.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_EXPLORATION_CONSTANT = 1.2
DEFAULT_RANDOM_SEED = 42


@dataclass
class Experiment:
    experiment_id: str
    kind: str
    origin: str | None
    status: str | None
    config_path: Path
    summary_dir: Path
    metric_name: str | None
    metric_value: float | None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    return data if isinstance(data, dict) else {}


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_metric(metrics: dict[str, Any]) -> tuple[str | None, float | None]:
    primary_metric = metrics.get("primary_metric")
    if isinstance(primary_metric, dict):
        name = primary_metric.get("name")
        value = _coerce_float(primary_metric.get("value"))
        return str(name) if name is not None else None, value
    value = _coerce_float(primary_metric)
    return None, value


def _infer_summary_dir(experiment_id: str, config_path: Path, config: dict[str, Any]) -> Path:
    implementation = config.get("implementation")
    if isinstance(implementation, dict):
        configured = implementation.get("summary_dir")
        if isinstance(configured, str) and configured.strip():
            return Path(configured)

    match = re.search(r"(\d+)", experiment_id)
    if match:
        suffix = config.get("name", config_path.stem)
        if isinstance(suffix, str) and suffix.strip():
            return Path("results") / f"exp_{int(match.group(1)):03d}_{suffix}"

    return Path("results") / config_path.stem


def _load_experiment(config_path: Path) -> Experiment | None:
    config = _load_yaml(config_path)
    if not config:
        return None

    experiment_id = config.get("id")
    if not isinstance(experiment_id, str) or not experiment_id.strip():
        match = re.match(r"(\d+)_", config_path.stem)
        if match:
            experiment_id = f"experiment_{int(match.group(1)):03d}"
        else:
            experiment_id = config_path.stem

    kind = config.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        kind = "baseline" if "baseline" in config_path.stem.lower() else "discovered"

    origin = config.get("origin")
    if origin is not None and not isinstance(origin, str):
        origin = str(origin)

    summary_dir = _infer_summary_dir(experiment_id, config_path, config)
    metrics = _load_yaml(Path(summary_dir) / "metrics.yaml")
    metric_name, metric_value = _extract_metric(metrics)
    status = metrics.get("status") or config.get("status")
    if status is not None and not isinstance(status, str):
        status = str(status)

    return Experiment(
        experiment_id=experiment_id,
        kind=kind,
        origin=origin,
        status=status,
        config_path=config_path,
        summary_dir=Path(summary_dir),
        metric_name=metric_name,
        metric_value=metric_value,
    )


def _normalized_ranks(values: dict[str, float], maximize: bool) -> dict[str, float]:
    if not values:
        return {}
    ordered = sorted(
        values.items(),
        key=lambda item: item[1],
        reverse=maximize,
    )
    if len(ordered) == 1:
        return {ordered[0][0]: 1.0}
    denominator = len(ordered) - 1
    ranks: dict[str, float] = {}
    for position, (experiment_id, _value) in enumerate(ordered):
        ranks[experiment_id] = 1.0 - (position / denominator)
    return ranks


def _resolve_candidates(config_dir: Path, require_origin: str | None) -> list[Experiment]:
    discovered: list[Experiment] = []

    for path in sorted(config_dir.glob("*.yaml")):
        if path.name in {"tracking.yaml", "remix.yaml"}:
            continue
        experiment = _load_experiment(path)
        if experiment is None:
            continue
        if experiment.kind == "baseline":
            continue
        if require_origin and experiment.origin != require_origin:
            continue
        if experiment.status != "completed" or experiment.metric_value is None:
            continue
        discovered.append(experiment)

    return discovered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Select one discovered experiment with UCT."
    )
    parser.add_argument(
        "--config-dir",
        default="config/exp",
        help="Directory containing experiment YAML configs.",
    )
    parser.add_argument(
        "--remix-config",
        default="config/exp/remix.yaml",
        help="Path to remix policy/state YAML.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override the remix random seed.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON result.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    remix_config = _load_yaml(Path(args.remix_config))
    policy = remix_config.get("policy")
    policy = policy if isinstance(policy, dict) else {}
    state = remix_config.get("state")
    state = state if isinstance(state, dict) else {}
    nodes = state.get("nodes")
    nodes = nodes if isinstance(nodes, dict) else {}

    objective_direction = str(policy.get("objective_direction", "maximize")).lower()
    maximize = objective_direction != "minimize"
    exploration_constant = float(
        policy.get("exploration_constant", DEFAULT_EXPLORATION_CONSTANT)
    )
    require_origin = None
    discovered_filter = policy.get("discovered_filter")
    if isinstance(discovered_filter, dict):
        origin = discovered_filter.get("require_origin")
        if isinstance(origin, str) and origin.strip():
            require_origin = origin

    discovered = _resolve_candidates(Path(args.config_dir), require_origin)
    if not discovered:
        raise SystemExit("No eligible discovered experiments found.")

    realized_values = {
        experiment.experiment_id: experiment.metric_value
        for experiment in discovered
        if experiment.metric_value is not None
    }
    normalized_ranks = _normalized_ranks(realized_values, maximize=maximize)

    total_visits = state.get("total_visits")
    if not isinstance(total_visits, int):
        total_visits = 0
    if total_visits <= 0:
        total_visits = sum(
            int(node.get("visits", 0))
            for node in nodes.values()
            if isinstance(node, dict) and isinstance(node.get("visits", 0), int)
        )
    total_visits = max(total_visits, 1)

    diagnostics: dict[str, dict[str, float | int | str | None]] = {}
    best_experiment: Experiment | None = None
    best_score = -math.inf

    uniform_prior = 1.0 / max(len(discovered), 1)
    for experiment in discovered:
        node_state = nodes.get(experiment.experiment_id)
        node_state = node_state if isinstance(node_state, dict) else {}
        visits = int(node_state.get("visits", 0))
        prior = _coerce_float(node_state.get("prior"))
        if prior is None:
            prior = uniform_prior
        value = normalized_ranks.get(experiment.experiment_id, 0.0)
        uct_score = value + exploration_constant * (
            prior * math.sqrt(total_visits) / (1 + visits)
        )

        diagnostics[experiment.experiment_id] = {
            "kind": experiment.kind,
            "origin": experiment.origin,
            "metric_name": experiment.metric_name,
            "metric_value": experiment.metric_value,
            "normalized_rank": round(value, 6),
            "prior": round(prior, 6),
            "visits": visits,
            "uct_score": round(uct_score, 6),
        }
        if uct_score > best_score:
            best_score = uct_score
            best_experiment = experiment

    if best_experiment is None:
        raise SystemExit("No eligible discovered experiments found.")

    seed = args.seed if args.seed is not None else int(policy.get("random_seed", DEFAULT_RANDOM_SEED))

    result = {
        "selector": "uct",
        "seed": seed,
        "objective_direction": objective_direction,
        "discovered_parent": best_experiment.experiment_id,
        "discovered_config": str(best_experiment.config_path),
        "diagnostics": diagnostics,
    }
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=args.pretty))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI guard
        print(str(exc), file=sys.stderr)
        raise
