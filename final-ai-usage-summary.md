# Final AI Usage Summary

## Tool used
**Cursor IDE** — AI agent mode for code generation and documentation.

## How AI was used (4 core prompts)
1. **Scaffold** — Project folder structure and `.cursorrules`
2. **Design** — `project-context.md` and `spec.md` from requirements
3. **Data generation** — `generate_sample_data.py` with intentional quality defects (seed 42)
4. **Pipeline implementation** — Bronze, Silver, Gold, dashboard layers, `schema.sql`, `README.md`

## Full prompt log
**`ai-prompts/all-project-prompts.md`** — 4 project-creation prompts only (excludes setup/debugging cross-questions).

## Key AI-assisted outcomes
- Medallion architecture: Bronze → Silver → Gold → Dashboard
- Silver flags bad rows via `quality_check_result` (never deletes)
- Config-driven paths in `pipeline_config.py`
- Sample data with documented defect counts for Silver validation

## Human involvement
- Created GitHub repo and Databricks workspace
- Ran notebook and validated Gold/dashboard query outputs
- Deployed on Databricks CE using Unity Catalog Volumes

## Repository
https://github.com/Rawat-A/C1-assessment
