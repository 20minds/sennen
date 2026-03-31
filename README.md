# Sennen

| <img src="assets/sennen.png" alt="Sennen logo" /> | `Sennen` is a Claude Code / Codex plugin for ML workflows. <br/><br/> It provides reusable skills for data access, visualization, train/test splits, metrics, baselines, experiments, review, data defect analysis, preprocessing, and explanation. <br/><br/> It is designed for Git, MLflow experiment tracking, DVC data versioning, and scientific data sources. |
| ------------------------------------------------------------- | ---------------------------- |

## Sennen Commands

Commands are either exposed as `/sen:*` slash commands or `$sen:*` skills. The `sen:*` skills are the source of truth; the Claude command files are thin wrappers around the matching skills.

- `sen:data` - connect and version scientific datasets
- `sen:visualize` - inspect data structure and distributions
- `sen:defects` - find defects in the data itself
- `sen:split` - create leakage-safe splits and test for leakage
- `sen:metrics` - define metrics, MLflow tracking, and result views
- `sen:baseline` - establish a baseline to beat
- `sen:preprocess` - clean data and engineer features
- `sen:experiment` - run and compare experiments
- `sen:review` - review the ML approach
- `sen:explain` - explain model behavior and feature importance

## Example: Clinical Trial Enrollment Predictor

Goal: predict whether a clinical trial is still open to enrollment 12 months after launch.

| Step | Command | Action |
| --- | --- | --- |
| 1 | `/sen:data` | ingest all ClinicalTrials.gov interventional studies |
| 2 | `/sen:data` | load the data into a flat modeling table |
| 3 | `/sen:visualize` | plot the enrollment survival curve |
| 4 | `/sen:defects` | check for defects in the trial dates, statuses, and enrollment fields |
| 5 | `/sen:split` | review the split for leakage and add an unseen-sponsor holdout |
| 6 | `/sen:metrics` | define the metric contract for month-12 open probability |
| 7 | `/sen:baseline` | build a baseline predictor and corresponding survival plots |
| 8 | `/sen:experiment` | improve the baseline with stronger text-based models |
| 9 | `/sen:experiment` | try a sentence embedding model and compare it against the sparse baseline |
| 10 | `/sen:explain` | explain the most important variables in the best model |
| 11 | `/sen:visualize` | plot survival curves for all experiments, ordered from baseline and then worst to best |

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

If you want Claude without `--plugin-dir`, use standalone project commands instead:

```bash
./setup --claude-standalone /your/data/folder
```

This installs project commands into `/Volume/repo/.claude/commands/`, so Claude can load them automatically when you start `claude` in that repo.

## Setup

When installing into a repo, `setup`:

- detects whether Git is already initialized
- asks before running `git init` if it is missing
- detects whether `.venv` already exists
- asks before running `uv venv .venv` if it is missing
- installs selected Python tooling into the repo with `uv add`
- creates `pyproject.toml` for `uv`-managed dependencies if needed
- does not support `requirements.txt` or `requirements.in` as setup-managed dependency files
- enables DVC when requested by installing `dvc` and optionally running `dvc init`
- installs `mlflow` when selected
- asks whether to enable MLflow when you do not specify `--mlflow` or `--no-tracking`
- adds conservative Python/ML `.gitignore`

For Claude repo installs, `setup` links the plugin into `plugins/sennen` and prints the corresponding `claude --plugin-dir ...` command.

For Claude standalone repo installs, `setup` writes project commands to `.claude/commands/`. This avoids `--plugin-dir`, but the commands are short standalone commands like `/data` and `/review`, not namespaced plugin commands like `/sen:data`.

You can also run it non-interactively:

```bash
./setup . --yes
./setup /Volume/repo --yes
./setup --codex /Volume/repo --yes
./setup --codex /Volume/repo --git --uv --dvc
./setup --codex /Volume/repo --git --uv --mlflow
./setup --codex /Volume/repo --no-git --no-uv --no-dvc
./setup --claude /Volume/repo --yes
./setup --claude-standalone /Volume/repo --yes
```

## Project Layout

`Sennen` uses normal repo folders for project artifacts:

```text
.
├── config/
│   ├── experiment/
│   ├── metrics/
│   │   └── metrics.yaml
│   ├── preprocess/
│   │   └── pipeline.yaml
│   └── split/
│       └── split.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/
├── models/
├── reports/
│   ├── data_quality/
│   ├── explanations/
│   ├── figures/
│   ├── review/
│   └── experiments_latest.md
└── src/
    ├── data/
    │   └── 001_*.py
    ├── experiment/
    │   └── 001_*.py
    ├── preprocess/
    │   └── 001_*.py
    └── visualize/
        └── 001_*.py
```

Those folders are conventions used by the skills. They are created by project work as needed, not by `setup`.

When `Sennen` downloads data into `data/raw/` or materializes outputs into `data/processed/` or `data/splits/`, those datasets should be tracked with DVC when DVC is available. Prefer `uv run dvc add data/` only when `data/` is intentionally one DVC-managed artifact boundary; otherwise track narrower directories. For experiment metrics, use MLflow to track runs in `sqlite:///mlflow.db`.

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
