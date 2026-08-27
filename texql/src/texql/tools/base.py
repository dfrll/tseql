#! /usr/bin/env python3

TOOL_REGISTRY = {}
LLM_SCHEMAS = []


def tool(
    name: str,
    description: str,
    parameters: dict,
    artifact_name: str,
    requires: list[str] | None = None,
):
    requires = requires or []

    def decorator(func):
        func.tool_name = name
        func.artifact_name = artifact_name
        func.requires = requires

        TOOL_REGISTRY[name] = func

        LLM_SCHEMAS.append(
            {
                "type": "function",
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        )

        return func

    return decorator
