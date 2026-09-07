# Pipeline task breakdown

## Completed

- [x] Project scaffold and `.cursorrules`
- [x] `project-context.md` and `spec.md`
- [x] Sample data generator + CSVs (`data/`)
- [x] Bronze ingestion (`src/bronze/`)
- [x] Silver quality checks (`src/silver/`)
- [x] Gold SQL + `create_gold_tables.py`
- [x] Dashboard queries + guide
- [x] `database/schema.sql` and `README.md`

## Run order (Databricks)

1. `python src/data_generation/generate_sample_data.py` (local)
2. `ingest_all.py` → Bronze Delta
3. `create_silver_tables.py` → Silver Delta + metrics report
4. `create_gold_tables.py` → Gold Delta
5. Dashboard queries in Databricks SQL

## Optional follow-ups

- [ ] Unity Catalog table registration
- [ ] Databricks job/workflow YAML
- [ ] Unit tests for quality-check counts vs `DATA_GENERATION_NOTES.md`
- [ ] Fill assessment docs (`reflection.md`, `candidate-info.md`, etc.)
