"""Tests for sen-data + db-clinicaltrials: 2024-2025 interventional studies.

Structural tests run without network access and verify the skill contracts.
LLM tests (marked with @pytest.mark.network @pytest.mark.llm) execute the sen-data
skill by invoking the `claude` CLI with `--plugin-dir`, letting Claude use its own
tools to download the data, then verifying that the artifact written to data/raw/
contains only interventional studies with start dates in 2024 or 2025.

Run structural only (default):
    uv run pytest tests/skills/test_sen_data_ct.py

Run all including LLM/network/claude:
    uv run pytest tests/skills/test_sen_data_ct.py -m "network"
    uv run pytest tests/skills/test_sen_data_ct.py -m "claude"
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "sennen"
SKILLS_DIR = PLUGIN_DIR / "skills"


# ---------------------------------------------------------------------------
# Structural tests — no network, no LLM
# ---------------------------------------------------------------------------


def test_sen_data_lists_clinicaltrials_skill() -> None:
    """sen-data skill must reference db-clinicaltrials in its Available Database Skills."""
    skill_md = (SKILLS_DIR / "sen-data" / "SKILL.md").read_text()
    assert "db-clinicaltrials" in skill_md


def test_db_clinicaltrials_skill_exists() -> None:
    """db-clinicaltrials skill must be present in sennen/skills/."""
    assert (SKILLS_DIR / "db-clinicaltrials" / "SKILL.md").exists()


def test_sen_data_required_outputs_include_data_raw() -> None:
    """sen-data Required Outputs section must promise artifacts under data/raw/."""
    skill_md = (SKILLS_DIR / "sen-data" / "SKILL.md").read_text()
    assert "data/raw/" in skill_md


def test_sen_data_ingestion_script_naming() -> None:
    """sen-data must specify numbered ingestion scripts (001_ingest.py pattern)."""
    skill_md = (SKILLS_DIR / "sen-data" / "SKILL.md").read_text()
    assert "001_ingest" in skill_md or "00x_" in skill_md


def test_sen_data_routes_to_db_skill_not_invented() -> None:
    """sen-data must instruct routing to db-* skills, not invent access patterns."""
    skill_md = (SKILLS_DIR / "sen-data" / "SKILL.md").read_text()
    assert "db-*" in skill_md


# ---------------------------------------------------------------------------
# LLM + network test — executes the sen-data skill via the claude CLI
# ---------------------------------------------------------------------------


@pytest.mark.network
@pytest.mark.claude
@pytest.mark.llm
def test_sen_data_skill_downloads_interventional_2024_2025(tmp_path: Path) -> None:
    """Execute /sen-data via the claude CLI to download 2024-2025 interventional studies.

    Invokes `claude --plugin-dir <sennen> -p "/sen-data ..."` so that Claude runs the
    skill end-to-end using its own tools (WebFetch, Write, Bash, etc.).

    Verifies the artifact written to data/raw/:
    - every record has studyType == INTERVENTIONAL
    - every record has a start date in 2024 or 2025
    """
    out_file = tmp_path / "data" / "raw" / "ct_interventional_2024_2025.jsonl"

    result = subprocess.run(
        [
            "claude",
            "--plugin-dir", str(PLUGIN_DIR),
            "--allowedTools", "Bash,Write,WebFetch",
            "--model", "sonnet",
            "-p",
            (
                "/sen-data Download exactly 100 interventional studies for 2024 "
                "(AREA[StartDate]RANGE[2024-01-01,2024-12-31] AND AREA[StudyType]INTERVENTIONAL, "
                "pageSize=100) and exactly 100 interventional studies for 2025 "
                "(AREA[StartDate]RANGE[2025-01-01,2025-12-31] AND AREA[StudyType]INTERVENTIONAL, "
                "pageSize=100) from the ClinicalTrials.gov API v2 "
                "(https://clinicaltrials.gov/api/v2/studies). "
                "Use the filter.advanced parameter. Do not paginate beyond the first page. "
                f"Append all 200 records as JSONL to: {out_file}"
            ),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"claude exited with {result.returncode}\n--- stderr ---\n{result.stderr}"
    )

    assert out_file.exists(), (
        f"/sen-data did not create the expected output: {out_file}\n"
        f"--- stdout ---\n{result.stdout}"
    )
    lines = out_file.read_text().splitlines()
    assert len(lines) == 200, f"Expected 200 records (100 per year), got {len(lines)}"

    for line in lines:
        record = json.loads(line)
        protocol = record.get("protocolSection", {})

        study_type = protocol.get("designModule", {}).get("studyType", "")
        assert study_type == "INTERVENTIONAL", f"Unexpected studyType: {study_type!r}"

        start_date = (
            protocol.get("statusModule", {}).get("startDateStruct", {}).get("date", "")
        )
        assert start_date, "Missing startDateStruct.date"
        start_year = int(start_date[:4])
        assert start_year in {2024, 2025}, (
            f"Start year {start_year!r} not in {{2024, 2025}} (date={start_date!r})"
        )

    print(f"\n  records downloaded and verified: {len(lines)}")
    print(f"  output: {out_file}")

    # --- /sen-split -----------------------------------------------------------
    split_result = subprocess.run(
        [
            "claude",
            "--plugin-dir", str(PLUGIN_DIR),
            "--allowedTools", "Bash,Read,Write,WebFetch",
            "--model", "sonnet",
            "-p",
            (
                f"/sen-split The dataset is at {out_file} "
                "(JSONL, one ClinicalTrials study per line). "
                "Design a valid train/test split. "
                "Write the split design to config/split/split.yaml. "
                "Include: strategy, train_ratio, the date column used, and leakage guards."
            ),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert split_result.returncode == 0, (
        f"claude /sen-split exited with {split_result.returncode}\n{split_result.stderr}"
    )

    split_yaml_path = tmp_path / "config" / "split" / "split.yaml"
    assert split_yaml_path.exists(), (
        f"/sen-split did not create config/split/split.yaml\n"
        f"--- stdout ---\n{split_result.stdout}"
    )

    import yaml  # noqa: PLC0415

    split_cfg = yaml.safe_load(split_yaml_path.read_text())

    strategy = str(split_cfg.get("strategy", "")).lower()
    assert any(kw in strategy for kw in ("temporal", "chronological", "time")), (
        f"Expected a temporal split strategy, got: {strategy!r}"
    )

    train_ratio = (
        split_cfg.get("train_ratio")
        or split_cfg.get("train_size")
        or split_cfg.get("train_fraction")
    )
    assert train_ratio is not None, (
        "config/split/split.yaml must include train_ratio, train_size, or train_fraction"
    )
    assert float(train_ratio) >= 0.5, (
        f"Train ratio {train_ratio} is below 0.5"
    )

    print(f"  split strategy: {strategy}")
    print(f"  train ratio: {train_ratio}")

    # --- /sen-metrics ---------------------------------------------------------
    metrics_result = subprocess.run(
        [
            "claude",
            "--plugin-dir", str(PLUGIN_DIR),
            "--allowedTools", "Bash,Read,Write,WebFetch",
            "--model", "sonnet",
            "-p",
            (
                f"/sen-metrics The dataset is at {out_file} "
                "(JSONL, one ClinicalTrials interventional study per line). "
                "The split config is at config/split/split.yaml. "
                "The prediction task is binary classification: predict whether a trial "
                "completes enrollment (overallStatus == COMPLETED vs other). "
                "Recommend evaluation metrics and write them to config/metrics/metrics.yaml."
            ),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert metrics_result.returncode == 0, (
        f"claude /sen-metrics exited with {metrics_result.returncode}\n{metrics_result.stderr}"
    )

    metrics_yaml_path = tmp_path / "config" / "metrics" / "metrics.yaml"
    assert metrics_yaml_path.exists(), (
        f"/sen-metrics did not create config/metrics/metrics.yaml\n"
        f"--- stdout ---\n{metrics_result.stdout}"
    )

    metrics_text = metrics_yaml_path.read_text().lower()
    assert "auc" in metrics_text, (
        f"Expected AUC in config/metrics/metrics.yaml, got:\n{metrics_yaml_path.read_text()}"
    )

    print(f"  metrics.yaml mentions AUC: True")
