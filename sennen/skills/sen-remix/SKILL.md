---
name: sen-remix
description: Create one new hybrid experiment by recombining a UCT-selected script with another randomly selected prior experiment, then run that remix and record the resulting artifacts.
---

# Sennen `/sen-remix`

Use this skill to perform one remix iteration end to end.

`sen-remix` is the search-and-synthesis skill in the Sennen workflow. It reads prior experiment metadata, uses the bundled UCT selector to choose the main script to improve, chooses a second prior experiment with ordinary Python randomness, recombines them into a single new candidate, runs that candidate, and writes the resulting artifacts.

## Role In The Workflow

`sen-remix` owns one full remix cycle:

1. prior experiments exist
2. `sen-remix` proposes the next hybrid candidate
3. `sen-remix` runs the candidate
4. reports and metrics capture the outcome
5. later, `sen-remix` can use those results to propose the next one

`sen-remix` must only claim results it actually ran and observed.
It may still report that a remix has been selected, recorded, and launched before the run has completed.

## Read First

Read these if they exist:

- `config/metrics/metrics.yaml`
- `config/split/split.yaml`
- `config/prepare/pipeline.yaml`
- `config/exp/remix.yaml`
- `config/exp/*.yaml`
- experiment summaries in `results/exp_00x_<label>/`
- `src/exp/*.py`

Prefer structured metadata in experiment YAML and metrics artifacts over markdown reports when choosing parents.

## Expected Experiment Layout

`sen-remix` should align with the existing Sennen repo shape:

- experiment configs: `config/exp/exp_00x_<label>.yaml`
- experiment code: `src/exp/exp_00x_<label>.py`
- large machine-readable outputs: `data/results/exp_00x_<label>/`
- machine-readable summaries: `results/exp_00x_<label>/metrics.yaml`
- experiment summaries: `results/exp_00x_<label>/summary.md`

`sen-remix` owns config, scaffold, execution, and rationale for the remix iteration it creates.
`sen-experiment` remains a sibling skill for general experiment work, but `sen-remix` should not depend on it to run the remix it just created.

## Parallel Execution Model

`sen-remix` may execute remix experiments in parallel, but it must dispatch them sequentially.

That means:

- only one active `sen-remix` dispatcher should read and update `config/exp/remix.yaml`
- visit counts must be updated before launching a new experiment
- background experiment runs may execute in parallel after dispatch
- background workers should write only to their own `data/results/exp_00x_<label>/` directories and their own summary pair under `results/exp_00x_<label>/`
- background workers should not directly mutate shared selection state such as total visits, priors, or other node bookkeeping

Treat `config/exp/remix.yaml` as single-writer selection state, `data/results/exp_00x_<label>/` as the source of large machine-readable result artifacts, and `results/exp_00x_<label>/metrics.yaml` as the default lightweight realized-result summary.

Do not treat an existing in-flight remix run as a reason to stop dispatching new work by default. After one remix is selected, recorded, and launched, `sen-remix` should continue dispatching additional remix runs until the configured concurrency target is reached.

Separate these two statements clearly:

- launch statement:
  - allowed immediately after dispatch
  - example: "experiment_022 was launched and is now in flight"
- outcome statement:
  - allowed only after outputs are observed
  - example: "experiment_022 improved ROC AUC to 0.87"

Do not wait for a launched run to finish merely because outcome claims require observed evidence.

## Selection Inputs

The bundled selector asset lives at:

- [`uct.py`](assets/uct.py)

It expects:

- per-experiment YAML in `config/exp/*.yaml`
- metrics in `results/exp_00x_<label>/metrics.yaml`
- UCT policy and visit state in `config/exp/remix.yaml`

The selector returns:

- one discovered experiment chosen with UCT
- score diagnostics as JSON

Use the asset rather than re-implementing UCT logic in prose. After it returns the primary script to improve, choose the second parent yourself from the eligible prior-experiment pool with ordinary Python randomness such as `random.choice` or `random.randint`.

Do not manually curate "interesting" or deliberately diverse parent pairs. Every remix parent pair must come directly from:

- one fresh `uct.py` selection for the primary parent
- one direct random draw for the secondary parent

## Required Outputs

Write exactly these artifacts for the remix iteration:

- next numbered experiment config in `config/exp/remix_00x.yaml`
- next numbered scaffold in `src/exp/exp_00x_remix.py`
- large execution artifacts in `data/results/exp_00x_remix/`
- machine-readable summary in `results/exp_00x_remix/metrics.yaml`
- concise rationale in `results/exp_00x_remix/summary.md`

## Selection Policy

Choose exactly two parents:

- one primary discovered experiment to improve
- one secondary prior experiment for recombination

Definitions:

- primary discovered experiment:
  - a prior non-baseline experiment
  - preferably marked with `origin: uct` or equivalent metadata
  - must have completed successfully
- secondary prior experiment:
  - any other eligible prior experiment, including a baseline or another discovered experiment
  - must not be the same experiment as the primary parent
  - should come from the same repo-local experiment pool being considered for remix

Default selection behavior:

1. run the UCT asset
2. use the returned discovered parent as the main script to improve
3. build the eligible secondary pool by scanning prior experiment configs
4. use ordinary Python randomness such as `random.choice(pool)` or `random.randint(0, len(pool) - 1)` to pick one secondary experiment from that pool
5. increment `state.total_visits` and the selected primary parent's visit count in `config/exp/remix.yaml`
6. if the repo tracks `in_flight`, increment it before launch
7. record the selection method and seed in the remix config
8. only then launch the remix run

If dispatching multiple remix runs, repeat the same mechanical process for each dispatch. Do not precompute a hand-picked set of pairings, remap seeds to preferred parents, or deliberately space out variants by judgment.

If the repo lacks enough structure to identify a primary discovered experiment and a secondary prior experiment confidently, say so and stop rather than guessing aggressively.

## Remix Strategy

The remix should be structured, not freeform.

Usually:

- keep the primary script skeleton unless the secondary experiment offers a clearly better stable structure
- import one or two promising mechanisms from the secondary experiment
- remove known-fragile or conflicting parts
- preserve the current split and metric contracts

The remix config must state:

- parent IDs
- why each parent was selected
- what remains from the primary script
- what is imported from the secondary experiment
- what is intentionally excluded
- what hypothesis the remix is testing
- what counts as success

## YAML Contract

Prefer a config shaped like this:

```yaml
id: experiment_002
name: remix_002
kind: remix
origin: sen-remix
parents:
  primary:
    id: experiment_014
    source: uct
  secondary:
    id: experiment_001
    source: python_random
selection:
  method: uct_plus_random_experiment
  seed: 42
hypothesis:
  statement: >
    Retaining the main training structure from experiment_014 while importing
    the stable preprocessing and evaluation choices from experiment_001 will
    improve the primary metric without increasing instability.
inheritance:
  keep_from_primary:
    - model_structure
    - main_training_flow
  import_from_secondary:
    - data_loading
    - split_contract
    - evaluation_flow
  exclude:
    - custom_posthoc_normalization
implementation:
  entrypoint: src/exp/exp_002_remix.py
  based_on: src/exp/exp_014_candidate.py
  data_results_dir: data/results/exp_002_remix
  summary_dir: results/exp_002_remix
success_criteria:
  primary_metric: must_exceed_baseline
  secondary_constraints:
    - runtime_within_1.5x_baseline
    - no_split_contract_changes
notes: []
```

Adapt field names to the repo if a clear experiment schema already exists. Prefer consistency over inventing new keys.

For selection state, prefer a `config/exp/remix.yaml` structure like:

```yaml
policy:
  selector: uct
  objective_direction: maximize
  exploration_constant: 1.2
  secondary_pool: completed_any
  random_seed: 42
  concurrency_target: 2

state:
  total_visits: 41
  nodes:
    experiment_014:
      visits: 7
      prior: 0.42
      in_flight: 1

history:
  - dispatched_experiment: experiment_022
    primary_parent: experiment_014
    secondary_parent: experiment_001
    status: launched
```

`visits` represent dispatches or expansions, not successful outcomes.
Realized performance should come from persisted run artifacts, especially `results/exp_00x_<label>/metrics.yaml`, not from duplicated values in `remix.yaml`.
Use `policy.concurrency_target` as the default upper bound for active remix runs. If fewer than that number are currently in flight, keep dispatching; do not wait for the earliest run to finish first.

## Scaffold Rules

The generated `src/exp/exp_00x_remix.py` should be a runnable scaffold, not an imaginary finished implementation.

Prefer:

- starting from the primary experiment structure selected by UCT
- marking remix insertion points clearly
- preserving metric and split contracts
- adding short comments only where the remix logic is not obvious

Do not fake successful implementation if the merge is unclear. If necessary, scaffold the file with explicit `TODO` markers and state the unresolved parts in the rationale report.

## Rationale Report

Write a short report to `results/exp_00x_remix/summary.md` containing:

- parent experiments chosen
- why they were chosen
- expected benefit of the remix
- what was actually run
- observed results and regressions
- likely failure modes
- what should be tried next if the remix underperforms

Keep it concise and operational.

## Workflow

1. Read current metric, split, preprocessing, experiment, and report artifacts.
2. Run the UCT selector asset against the repo-local experiment metadata.
3. Use the returned discovered experiment as the primary script to improve.
4. Build the eligible secondary pool and choose one parent with ordinary Python randomness.
5. Read the source code of both selected parent experiments from `src/exp/` before proceeding.
6. Extract what each parent contributes.
7. Define one concrete remix hypothesis.
8. Write the next numbered remix YAML config.
9. Write the next numbered experiment scaffold.
10. Update shared selection state in `config/exp/remix.yaml` before launch.
11. Run the remix candidate in the repo's standard environment.
12. Record and report the launch immediately as an in-flight remix dispatch.
13. If fewer than the configured number of remix runs are in flight, continue dispatching additional remix runs without waiting for earlier ones to finish.
14. If multiple remix runs are active, keep them isolated by writing only to their own `data/results/exp_00x_<label>/` directories and their own `results/exp_00x_<label>/summary.md` and `metrics.yaml` pair.
15. Write large machine-readable outputs under `data/results/exp_00x_<label>/`.
16. Write lightweight summaries such as metrics and runtime to `results/exp_00x_remix/metrics.yaml`.
17. Write the rationale report with actual observed results once they exist.
18. If the remix could not be run, say so explicitly and explain the blocker.

## Example Selector Invocation

If the repo uses a local virtualenv, a typical invocation is:

```bash
uv run python  \
  assets/uct.py \
  --config-dir config/exp \
  --remix-config config/exp/remix.yaml \
  --pretty
```

If the repo uses `uv`, prefer:

```bash
uv run python assets/uct.py \
  --config-dir config/exp \
  --remix-config config/exp/remix.yaml \
  --pretty
```

Then choose the second experiment in ordinary Python, for example:

```python
import random

secondary_parent = random.choice(eligible_experiments)
```

Use the host repo's actual skill install path when running the asset from a plugin checkout.

## Rules

- Do not invent prior scores, provenance, or parent quality if they are missing.
- Use `uct.py` for the primary script choice and ordinary Python randomness such as `random.choice` or `random.randint` for the secondary choice rather than inventing an alternative selection rule ad hoc.
- Do not manually choose parent pairs for variety, coverage, or taste; rely on `uct.py` and a direct random draw every time.
- Do not pre-map random seeds to desired secondary parents or use seeds as a hidden manual selection mechanism.
- If remix runs are launched in parallel, keep dispatch sequential and update visits before launching the run.
- Do not block new dispatches merely because one remix run is still in flight; continue until the configured concurrency target is reached.
- It is valid to report launch status for in-flight remix runs even when outcome metrics are not yet available.
- Only outcome claims, regressions, or improvements require observed results.
- Prefer tracking `in_flight` in `config/exp/remix.yaml` when multiple remix runs may be active at once.
- Do not let background workers mutate shared UCT state directly.
- Do not overwrite prior experiment artifacts without clear reason.
- Prefer one high-quality remix over several weak remixes.
- Keep the remix compatible with the current repo’s metric, split, preprocessing, DVC, and MLflow conventions.
- Actually run the remix before describing its outcome.
- If the current repo lacks enough prior experiments to perform a meaningful remix, say so directly.

## Examples

Typical user intents:

- “Remix one of our stronger experiments with a baseline.”
- “Create the next hybrid candidate from prior runs.”
- “Take a UCT-discovered experiment and combine it with a stable baseline.”
