#! /usr/bin/env python3
import json
import polars as pl
from structlog.stdlib import BoundLogger
from .tools.base import LLM_SCHEMAS, TOOL_REGISTRY
from typing import Any


SYSTEM_PROMPT = """
You have access to function tools.

Call the sql tool to retrieve either spefific dataset characteristics or to run a query.
Do not invent database results.
"""


def _extract_calls(response):
    return [o for o in response.output if o.type == "function_call"]


def _parse_args(call):
    return json.loads(call.arguments or "{}")


def _get_table_payload(
    artifact_name: str,
    result: pl.DataFrame,
    max_rows: int,
    log: BoundLogger,
) -> dict:
    preview = result.head(max_rows)

    log.info(
        "jsonify_dataframe",
        artifact_name=artifact_name,
        dimensions=result.shape,
        effective_max_rows=preview.height,
        max_rows_allowed=max_rows,
    )

    return {
        "artifact": artifact_name,
        "columns": preview.columns,
        "rows": preview.to_dicts(),
        "preview_count": preview.height,
        "row_count": result.height,
    }


def run_agent(user_msg, services, config, base_log):

    model = config.default_model

    response = services.llm.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_msg,
            },
        ],
        tools=LLM_SCHEMAS,
    )

    artifacts = {}
    max_steps = 5

    for step in range(max_steps):
        step_log = base_log.bind(step=step)
        calls = _extract_calls(response)

        if not calls:
            step_log.info("no_more_tool_calls")
            break

        tool_outputs = []
        step_log.info("tool_calls", calls=[c.name for c in calls])

        for call in calls:
            tool_func = TOOL_REGISTRY.get(call.name)
            args = _parse_args(call)

            if not tool_func:
                step_log.warning(
                    "tool_not_found",
                    tool=call.name,
                )
                continue

            result = tool_func(
                args=args,
                artifacts=artifacts,
                services=services,
                log=step_log,
            )

            artifacts[tool_func.artifact_name] = result

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(
                        {
                            "artifact": tool_func.artifact_name,
                            "row_count": getattr(result, "height", 0),
                            "result": result.write_json(),
                        }
                    ),
                }
            )

        response = services.llm.responses.create(
            model=model,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=LLM_SCHEMAS,
        )

    # last DataFrame artifact,
    table = None

    for artifact_name, artifact in reversed(list(artifacts.items())):
        if isinstance(artifact, pl.DataFrame):
            table = _get_table_payload(
                artifact_name=artifact_name,
                result=artifact,
                max_rows=100,
                log=base_log,
            )
            break

    return {
        "reply": response.output_text or "Done.",
        "table": table,
    }
