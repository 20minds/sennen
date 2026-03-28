# `/sen:metrics`

Select evaluation metrics, configure MLflow tracking, and inspect tracked results.

Write the metric contract in `config/metrics/metrics.yaml`. Make the primary metric explicit, add supporting metrics where needed, and keep reporting aligned with the split strategy and task type. Use MLflow when the repo already uses it or the user explicitly asks for tracked runs, and prefer `sqlite:///mlflow.db` over file-backed metadata for local setups. If the user asks to view results, inspect the current MLflow runs and summarize the tracked metrics.
