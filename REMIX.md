# Sennen Remix

Progress rarely comes from truly novel ideas — more often than not it comes from combining the right existing ones. Sennen remix applies this principle to ML experiments: rather than asking you to guess what to try next, it searches your prior runs systematically and proposes the next hybrid candidate automatically.

## The Problem

ML research involves a lot of trial and error. After running a handful of experiments, you face a recurring question: *what should I try next?* The naive answer is intuition — pick something that seems promising. The challenge is that intuition is slow, biased, and doesn't scale.

## The Inspiration: AlphaZero

AlphaZero learned to play chess without human knowledge by combining two ideas:

- **Self-play** — generate experience by playing against itself
- **Tree search** — use past results to decide which moves to explore next, balancing promising lines against unexplored ones

Remix borrows the tree-search idea, not self-play. Your experiments are the moves; their measured outcomes are the scores. The analogy has limits — experiment space has no fixed branching structure, and there is no opponent — but the core tension between exploiting what works and exploring what hasn't been tried yet is the same.

## How It Works

Each remix cycle has two selection steps followed by a merge:

```
prior experiments
      │
      ▼
  uct.py ──► primary parent (high score, underexplored)
      │
      ▼
random choice ──► secondary parent (any other prior experiment)
      │
      ▼
  read both source files
      │
      ▼
  hybrid scaffold ──► run ──► record results
      │
      ▼
  update visit counts ──► next iteration
```

**Primary selection** runs `uct.py`, which scores each prior experiment using its measured metric and how many times it has already been selected. Experiments with good results that haven't been explored much score highest.

**Secondary selection** draws one experiment at random from the remaining pool with `random.randint`. This is intentionally unguided — it prevents the search from collapsing into variations on a single lineage.

**Merging** is done by an LLM agent that reads both source files in full. The primary parent provides the skeleton — training loop, model structure, overall flow. The secondary parent contributes one or two specific mechanisms: a preprocessing step, an evaluation strategy, a regularisation choice. The agent writes a new numbered scaffold and records exactly what was kept, imported, and excluded.

## Why UCT?

UCT (Upper Confidence Bound for Trees) scores each candidate as:

```
score = mean_metric + C * sqrt(log(total_visits) / node_visits)
```

- The first term favours experiments with strong results (**exploitation**)
- The second term favours experiments that haven't been selected much yet (**exploration**)
- `C` is a tunable exploration constant (default 1.2)

Without exploration the search fixates on a local optimum. Without exploitation it becomes random. UCT keeps both in tension automatically, and the balance shifts naturally as visits accumulate.

The selector script is named `uct.py` because the formula supports an optional prior term — but since sen-remix does not have a learned predictor, it runs as standard UCT with a uniform prior.

Visit counts represent dispatches, not successful outcomes. Realized performance comes from the metrics recorded after each run.

## What Gets Combined

The merge is structured, not freeform. Each remix config records:

- which parents were chosen and why
- what was kept from the primary
- what was imported from the secondary
- what was intentionally excluded
- the hypothesis being tested
- what counts as success

The metric contract and split contract are always preserved. The scaffold is a real runnable file, not a sketch — if the merge is genuinely ambiguous, the agent marks the unresolved parts with explicit `TODO` comments rather than silently guessing.

## Scope

- Remix does not invent new architectures from scratch
- It does not guarantee improvement on any single run — it improves the *expected* yield of a search over many runs
- It is not a hyperparameter tuner
- It does not replace understanding your data or defining the right metric
- It requires at least a few prior experiments with meaningful, comparable results to work well

The claim that remix finds better combinations faster than manual iteration is a reasonable prior, not a proven result. Its value accumulates over many iterations, not in a single cycle.

## Prerequisites

- A Sennen project with at least two completed prior experiments
- Experiment configs in `config/exp/*.yaml`
- Metrics recorded in `results/exp_00x_<label>/metrics.yaml`
- Selection state in `config/exp/remix.yaml`

## Getting Started

Run the remix skill from within a Sennen project:

```
/sen-remix
```

The skill handles selection, scaffolding, execution, and record-keeping automatically.
