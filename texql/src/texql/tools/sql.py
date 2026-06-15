#! /usr/bin/env python3
import polars as pl
from structlog.stdlib import BoundLogger
from .base import tool
from ..config import Services


@tool(
    name="sql",
    description=(
        "Generate a valid SQLite query on the `metadata` table whenever the user query is about metadata. "
        "There is exactly one table: metadata. Never query any other table name. "
        "Requirements: "
        "1. For row-level queries, SELECT must always include project (dataset ids) and external_id (sample ids). "
        "2. For aggregate queries (COUNT, SUM, AVG, DISTINCT), return only the aggregate columns (do not join with project, external_id, biosample). "
        "3. Use WHERE clauses to filter results before selecting. "
        "4. Never use SELECT *. Always name columns explicitly. "
        "5. Ensure valid SQLite syntax. "
        "Schema: "
        "biosample, insdc_first_public, ena_first_public, common_name, ena_first_public_1, source_name, treatment, "
        "biomaterial_provider, scientific_name, age, submitter_id, tissue, insdc_last_update, cell_type, sex, "
        "external_id, ena_checklist, sample_name, insdc_center_name, genotype, individual, broker_name, isolate, "
        "cell_line, ena_last_update, disease, dev_stage, insdc_status, sample_type, insdc_center_alias, ena_last_update_1, "
        "run, releasedate, loaddate, spots, bases, spots_with_mates, avglength, size_mb, assemblyname, download_path, experiment, "
        "libraryname, librarystrategy, libraryselection, librarysource, librarylayout, insertsize, insertdev, platform, model, "
        "project, bioproject, study_pubmed_id, projectid, sample, sampletype, taxid, scientificname, samplename, g1k_pop_code, "
        "source, g1k_analysis_group, subject_id, sex_right, disease_right, tumor, affection_status, analyte_type, histological_type, "
        "body_site, centername, submission, dbgap_study_accession, consent, runhash, readhash"
    ),
    parameters={
        "type": "object",
        "properties": {
            "sql_query": {"type": "string"},
        },
        "required": ["sql_query"],
    },
    artifact_name="sql_result",
)
def sql(
    args: dict,
    artifacts: dict,
    services: Services,
    log: BoundLogger,
):
    sql_query = args.get("sql_query")
    # if not sql_query:
    # raise ToolError(
    # code="missing_sql_query",
    # message="SQL query is required.",
    # retryable=False,
    # )

    log.info("execute_sql_query", sql_query=sql_query)

    # try:
    page = services.query_d1(sql_query)
    # except Exception as e:
    # raise ToolError(
    # code="d1_query_failure",
    # message="D1 query execution failed",
    # retryable=True,
    # ) from e

    if not page or not getattr(page, "result", None):
        return pl.DataFrame()

    first_page = page.result[0]

    results = getattr(first_page, "results", None)
    # if results is None:
    # raise ToolError(
    # code="invalid_query_result_format",
    # message="D1 returned an unexpected result structure.",
    # retryable=False,
    # )

    # if not isinstance(results, list):
    # raise ToolError(
    # code="invalid_query_result_format",
    # message="D1 results are not a list.",
    # retryable=False,
    # )

    if not results:
        return pl.DataFrame()

    return pl.from_dicts(results, infer_schema_length=len(results))
