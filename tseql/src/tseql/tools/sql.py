#! /usr/bin/env python3
import yaml
import polars as pl
from pathlib import Path
from structlog.stdlib import BoundLogger
from .base import tool
from ..config import Services


with open(Path(__file__).parent / "sql.yaml") as f:
    tool_yaml = yaml.safe_load(f)


@tool(
    name="sql",
    description=(tool_yaml["description"]),
    parameters={
        "type": tool_yaml["parameters"]["type"],
        "properties": tool_yaml["parameters"]["properties"],
        "required": tool_yaml["parameters"]["required"],
    },
    artifact_name=tool_yaml["artifact_name"],
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
