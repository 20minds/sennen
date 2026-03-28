# `/sen:preprocess`

Clean data and engineer features.

Create preprocessing code in `src/preprocess/001_preprocess.py` or the next numbered file. Materialize outputs in `data/processed/`. If DVC is available, prefer `uv run dvc add data/` when `data/` is the intended DVC artifact boundary; otherwise use `uv run dvc add data/processed/`. Verify with `uv run dvc status`.
