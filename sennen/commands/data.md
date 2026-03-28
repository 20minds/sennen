# `/sen:data`

Connect and version scientific datasets.

Use repo-native layout:
- raw inputs in `data/raw/`
- ingestion code in `src/data/001_ingest.py` or the next numbered file

Prefer Git for code and metadata. If DVC is available, prefer `uv run dvc add data/` when `data/` is meant to be one DVC-managed artifact boundary; otherwise use a narrower target such as `uv run dvc add data/raw/`. Verify with `uv run dvc status`. If a Python package is needed, add it instead of dropping the approach. If the repo uses `uv`, add project packages with `uv add`.
