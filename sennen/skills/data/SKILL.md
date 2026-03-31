---
name: sen:data
description: Connect scientific data sources with Git and DVC-aware workflows.
---

# Sennen `/data`

Use this skill when the user needs to discover, inspect, or ingest scientific data.

## Read First

- existing ingestion code under `src/data/`
- existing data directories under `data/`
- existing DVC files such as `.dvc`, `dvc.yaml`, and `dvc.lock`
- available `db-*` skills when the source is a supported scientific database

## Available Database Skills

When the data source is a supported scientific database, use the matching `db-*` skill for source-specific access patterns, query parameters, export formats, and API quirks.

Examples:
- `db-clinicaltrials`
- `db-pubmed`
- `db-chembl`
- `db-uniprot`
- `db-opentargets`
- `db-geo`

## Required Outputs

- raw source artifacts under `data/raw/`
- optional ingestion code in `src/data/00x_*.py`
- optional schema or source notes in `reports/data_quality/` or `reports/review/`

## Workflow

1. Inspect the current repo for data loaders, DVC files, dataset manifests, notebooks, and raw data references.
2. Identify the source type and access pattern.
3. If the source matches a supported scientific database, use the corresponding `db-*` skill. These `db-*` entries are skills, not just naming conventions.
4. Recommend or implement a Git and DVC-friendly way to version dataset metadata and artifacts.
5. Store raw inputs under `data/raw/`.
6. If new ingestion code is needed, create `src/data/001_ingest.py` or the next available numbered file.
7. If new raw data was downloaded and DVC is available, track it with DVC.

## Examples

- Git: commit dataset manifests, schema notes, and loader code; do not commit large raw data blobs.
- DVC: inspect `dvc.yaml`, `.dvc` files, and `dvc.lock`; prefer `dvc pull` for existing tracked artifacts. For clean repos where `data/` is intended to be one DVC-managed artifact boundary, prefer `uv run dvc add data/`, then check `uv run dvc status`. If `data/` already contains mixed Git-tracked metadata or existing `.dvc` files, prefer narrower boundaries such as `uv run dvc add data/raw/`.
- `uv`: prefer keeping reproducible dataset tooling inside the repo's managed `uv` environment when the project already uses `uv`.
- Scientific sources: be explicit about source-specific access notes such as Hugging Face datasets, OpenML, S3 buckets, institutional CSV exports, microscopy TIFF folders, HDF5, NetCDF, FASTA, AnnData, or parquet tables.
- Database-skill routing: for ClinicalTrials.gov use the `db-clinicaltrials` skill; for PubMed use `db-pubmed`; for ChEMBL use `db-chembl`; for UniProt use `db-uniprot`; for Open Targets use `db-opentargets`; for GEO use `db-geo`.

## Rules

- Prefer reproducible, versioned access paths over ad hoc manual downloads.
- When a matching `db-*` skill exists, use that skill for source-specific querying, filtering, and export details instead of inventing a generic access pattern.
- If the repo already uses DVC, preserve that workflow.
- If the repo does not use DVC, do not introduce it unless the user asked for it or the workflow clearly benefits.
- Before running `uv run dvc add data/`, inspect whether `data/` is already a mixed Git/DVC boundary. If it is, prefer subdirectories such as `data/raw/` instead of taking over the whole tree.
- Prefer `data/raw/` for source data, not hidden plugin directories.
- Prefer numbered ingestion scripts such as `src/data/001_ingest.py`, `src/data/002_openml_import.py`, or `src/data/003_hf_download.py`.
- If extra Python packages are needed, install them instead of removing the dependency from the workflow.
- If the repo uses `uv`, add those packages with `uv add`.
- When data is downloaded into `data/raw/` and DVC is available, run DVC tracking for those artifacts rather than leaving them unversioned. Prefer `uv run dvc add data/` when `data/` is meant to be one DVC-managed artifact boundary; otherwise prefer `uv run dvc add data/raw/`. In both cases, verify with `uv run dvc status`.
