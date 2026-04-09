# Sennen

| <img src="assets/sennen.png" alt="Sennen logo" /> | `Sennen` is a Claude Code / Codex plugin for ML workflows. <br/><br/> It provides reusable skills for repo diagnosis, planning, data access, joining meetings, visualization, train/test splits, metrics, baselines, experiments, review, data defect analysis, preprocessing, and explanation. <br/><br/> It is designed for Git, MLflow experiment tracking, DVC data versioning, and scientific data sources. |
| ------------------------------------------------------------- | ---------------------------- |

## Sennen Commands

In Claude, skills are exposed as `/sen-*` and `/db-*`. In Codex, skills are available as `$sen-*` and `$db-*`.

### High-Level Commands

- `sen-data` - connect and version scientific datasets
- `sen-plan` - define the prediction task, split strategy, and metric contract
- `sen-experiment` - run the first baseline or compare later experiments
- `sen-review` - review the ML approach

### Specialist Commands

- `sen-defects` - find defects in the data itself
- `sen-visualize` - inspect data structure and distributions
- `sen-split` - create leakage-safe splits and test for leakage
- `sen-metrics` - define metrics, MLflow tracking, and result views
- `sen-preprocess` - clean data and engineer features
- `sen-explain` - explain model behavior and feature importance
- `sen-join` - join a Google Meet URL in guest mode
- `sen-doctor` - diagnose and repair repo readiness for the Sennen workflow

## Example: Clinical Trial Enrollment Predictor

Goal: predict whether a clinical trial is still open to enrollment 12 months after launch.

| Step | Command | Action |
| --- | --- | --- |
| 1 | `/sen-data` | ingest all ClinicalTrials.gov interventional studies |
| 2 | `/sen-data` | load the data into a flat modeling table |
| 3 | `/sen-plan` | define the month-12 target, leakage-safe holdout, and metric contract |
| 4 | `/sen-visualize` | plot the enrollment survival curve |
| 5 | `/sen-experiment` | build a baseline predictor and corresponding survival plots |
| 6 | `/sen-experiment` | improve the baseline with stronger text-based models |
| 7 | `/sen-experiment` | try a sentence embedding model and compare it against the sparse baseline |
| 8 | `/sen-explain` | explain the most important variables in the best model |
| 9 | `/sen-review` | critique the workflow, results, and next actions |

## Data Versioning and Experiment Tracking

`Sennen` treats data versioning and experiment tracking separately:

- DVC tracks downloaded and generated datasets in `data/raw/`, `data/processed/`, and optionally `data/splits/`.
- MLflow is the supported experiment metrics backend.
- `setup` manages Python dependencies through `uv` and `pyproject.toml` only.

## Install

```bash
git clone https://github.com/20minds/sennen.git
cd sennen

./setup /your/data/folder
```

```bash
cd /your/data/folder

claude --plugin-dir plugins/sennen

OR

codex
```

Repo-local setup installs:

- Claude plugin files into `plugins/sennen`
- Codex skills into `.agents/skills`

Global setup installs:

- Claude skills into `~/.claude/skills`
- Codex skills into `~/.codex/skills`

If you want Claude without `--plugin-dir`, use standalone project commands instead:

```bash
./setup --claude-standalone /your/data/folder
```

This installs project commands into `/your/data/folder/.claude/commands/` and the matching skill bundles into `/your/data/folder/.claude/skills/`, so Claude can load them automatically when you start `claude` in that repo.

`setup` now also asks whether to install:

- the optional `db-*` scientific database skills
- the optional `sen-join` conference-call skill

If you choose `sen-join`, setup will look for `TWENTYMINDS_API_KEY` in the environment or repo `.env`, and it can prompt you to save one. The skill is still installed even if no key is available yet.

You can also run it non-interactively:

```bash
./setup . --yes
./setup /your/data/folder --yes
./setup --codex /your/data/folder --yes
./setup --codex /your/data/folder --git --uv --dvc
./setup --codex /your/data/folder --git --uv --mlflow
./setup --codex /your/data/folder --no-git --no-uv --no-dvc
./setup --claude /your/data/folder --yes
./setup --claude-standalone /your/data/folder --yes
```

## Project Layout

`Sennen` uses normal repo folders for project artifacts:

```text
.
├── config/
│   ├── exp/
│   │   ├── exp_001_baseline.yaml
│   │   ├── remix.yaml
│   │   └── tracking.yaml
│   ├── metrics/
│   │   └── metrics.yaml
│   ├── prepare/
│   │   └── pipeline.yaml
│   └── split/
│       └── split.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── results/
│   │   └── exp_001_baseline/
│   └── splits/
├── models/
│   ├── checkpoints/
│   └── exports/
├── results/
│   └── exp_001_baseline/
│       ├── metrics.yaml
│       └── summary.md
│   ├── data_quality/
│   ├── explanations/
│   ├── figures/
│   ├── review/
└── src/
    ├── data/
    │   └── data_001_ingest.py
    ├── exp/
    │   └── exp_001_baseline.py
    ├── lib/
    ├── prepare/
    │   └── prep_001_pipeline.py
    └── visualize/
        └── vis_001_inspect.py
```

Those folders are conventions used by the skills. They are created by project work as needed, not by `setup`.

Suggested use:

- `config/exp/exp_001_baseline.yaml` stores the first baseline as a normal experiment config
- later baselines can be added as `config/exp/exp_00x_<label>.yaml` with `kind: baseline`
- use `reference_role: primary` to mark the default baseline comparison anchor when multiple baselines exist
- `config/exp/tracking.yaml` stores MLflow tracking conventions such as `sqlite:///mlflow.db`
- `results/exp_001_baseline/summary.md` and later `results/exp_00x_<label>/summary.md` files store human-readable experiment summaries
- `results/exp_001_baseline/metrics.yaml` and later `results/exp_00x_<label>/metrics.yaml` files store Git-friendly machine-readable summaries such as metrics and runtime
- `src/lib/` stores shared utilities that should not live in numbered workflow scripts
- `src/exp/` stores sortable experiment entrypoints such as `exp_001_baseline.py`
- `data/results/exp_00x_<label>/` stores large DVC-friendly prediction and evaluation artifacts
- the default Git-friendly experiment summary pair lives under `results/exp_00x_<label>/`

When `Sennen` downloads data into `data/raw/` or materializes outputs into `data/processed/` or `data/splits/`, those datasets should be tracked with DVC when DVC is available. Prefer `uv run dvc add data/` only when `data/` is intentionally one DVC-managed artifact boundary; otherwise track narrower directories. For experiment metrics, use MLflow to track runs in `sqlite:///mlflow.db`.

## High-Level Workflow

These high-level commands are the recommended entry points:

| Command | Purpose | Maps to lower-level commands |
| --- | --- | --- |
| `/sen-plan` | Define the task, leakage-safe evaluation setup, and metric contract | `/sen-doctor`, `/sen-defects`, `/sen-split`, `/sen-metrics`, optionally `/sen-visualize` |
| `/sen-data` | Ingest, inspect, and version data | `/sen-data`, optionally `/sen-defects`, `/sen-visualize`, and relevant `db-*` skills |
| `/sen-experiment` | Run the first baseline when none exists, or run stronger models against the baseline afterward | `/sen-experiment`, optionally `/sen-preprocess`, `/sen-visualize`, `/sen-explain` |
| `/sen-review` | Critique the approach, results, and next steps | `/sen-review`, optionally `/sen-experiment`, `/sen-visualize`, `/sen-explain` |

`/sen-doctor` is a specialist diagnosis and repair command. Use it directly when you want to prepare or validate repo structure, DVC readiness, or MLflow readiness before higher-level workflow steps.

`/sen-join` is a specialist utility command. It sends a request to the 20minds meeting-bot endpoint for a Google Meet URL and is intentionally separate from the main ML workflow commands.

## Scientific Database Skills

`Sennen` also includes scientific database skills for:

| Skill | Purpose |
| --- | --- |
| `db-alphafold` | Retrieve AlphaFold predicted protein structures, coordinates, and confidence metrics by UniProt ID. |
| `db-biorxiv` | Search bioRxiv preprints by topic, author, category, or date and retrieve metadata or PDFs. |
| `db-chembl` | Query ChEMBL compounds, targets, and bioactivity data for SAR and medicinal chemistry work. |
| `db-clinicaltrials` | Search ClinicalTrials.gov trials by condition, drug, status, phase, or NCT ID. |
| `db-clinpgx` | Access ClinPGx pharmacogenomics data for gene-drug interactions, allele functions, and CPIC guidance. |
| `db-clinvar` | Retrieve ClinVar variant significance and pathogenicity annotations for genomic interpretation. |
| `db-cosmic` | Query COSMIC somatic mutation, gene fusion, and cancer gene data for oncology research. |
| `db-drugbank` | Access DrugBank drug properties, targets, interactions, pathways, and pharmacology data. |
| `db-ena` | Retrieve ENA sequence records, raw reads, and assemblies by accession for genomics workflows. |
| `db-ensembl` | Query Ensembl genes, variants, orthologs, sequences, and comparative genomics data. |
| `db-fda` | Search openFDA drugs, devices, adverse events, recalls, and regulatory submission data. |
| `db-gene` | Retrieve NCBI Gene annotations, identifiers, locations, phenotypes, and related records. |
| `db-geo` | Search and download GEO expression and genomics datasets such as GSE, GSM, and GPL records. |
| `db-gwas` | Query GWAS Catalog variant-trait associations, p-values, and genetics evidence. |
| `db-hmdb` | Access HMDB metabolites, chemical properties, biomarker data, spectra, and pathways. |
| `db-kegg` | Query KEGG pathways, gene mappings, drug interactions, and identifier conversions. |
| `db-metabolomics-workbench` | Access Metabolomics Workbench studies, RefMet data, spectra, and metabolite metadata. |
| `db-opentargets` | Query Open Targets target-disease associations, tractability, safety, and drug evidence. |
| `db-pdb` | Search and download RCSB PDB macromolecular structures and metadata. |
| `db-pubchem` | Query PubChem compounds, properties, similarity, substructure, and bioactivity data. |
| `db-pubmed` | Search PubMed literature with Boolean and MeSH queries and retrieve article metadata. |
| `db-string` | Query STRING protein-protein interactions, networks, and enrichment results. |
| `db-uniprot` | Access UniProt protein records, FASTA sequences, and ID mapping workflows. |
| `db-uspto` | Search USPTO patent, trademark, assignment, and prosecution history data. |
| `db-zinc` | Access ZINC purchasable compounds and 3D-ready structures for screening and docking. |
