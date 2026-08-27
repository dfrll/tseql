#! /usr/bin/env python3
import polars as pl
from structlog.stdlib import BoundLogger
from .base import tool
from ..config import Services


@tool(
    name="sql",
    description=(
        "Generate a valid SQLite query on the table whenever the user asks. "
        "There is exactly one table. Never query any other table name. "
        "Requirements: "
        "1. For row-level queries, SELECT must always be present."
        "2. For aggregate queries (COUNT, SUM, AVG, DISTINCT), return only the aggregate columns. "
        "3. Use WHERE clauses to filter results before selecting. "
        "4. Never use SELECT *. Always name columns explicitly. "
        "5. Ensure valid SQLite syntax. "
        "Schema: "
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
