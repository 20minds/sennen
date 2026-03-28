# `/sen:experiment`

Run and compare experiments.

Create experiment code in `src/experiment/001_baseline.py` or the next numbered file and keep reports in `reports/`. Track large models, predictions, and result artifacts with DVC when available. Use MLflow when the repo already uses it or when the user explicitly wants MLflow-style run tracking, and prefer `sqlite:///mlflow.db` for local metadata.
