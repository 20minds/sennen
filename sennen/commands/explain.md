# `/sen:explain`

Explain model behavior and feature importance.

Prefer the simplest correct explanation method:
- coefficients or model-native importance when reliable
- permutation importance when model-agnostic comparison is enough
- SHAP when local or global contribution analysis is actually needed and practical

Write notes in `reports/explanations/001_initial_explanation.md` or the next numbered report. Put executable analysis in `src/visualize/001_explain.py` or the next numbered file. If explanation outputs are large and DVC is available, track them with DVC.
