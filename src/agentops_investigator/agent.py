import json
from typing import Any, Callable

from agentops_investigator.llm import ToolResult, create_llm_provider
from agentops_investigator.tools.definitions import TOOLS
from agentops_investigator.tools.operations import (
    get_service_config,
    get_service_deployments,
    get_service_health,
    get_service_logs,
    get_service_metrics,
    list_services,
)


TOOL_HANDLERS: dict[str, Callable[..., Any]] = {
    "list_services": list_services,
    "get_service_health": get_service_health,
    "get_service_logs": get_service_logs,
    "get_service_metrics": get_service_metrics,
    "get_service_deployments": get_service_deployments,
    "get_service_config": get_service_config,
}


def execute_tool(
    name: str,
    arguments: dict[str, Any],
) -> Any:
    handler = TOOL_HANDLERS.get(name)

    if handler is None:
        raise ValueError(f"Unknown tool: {name}")

    return handler(**arguments)


INSTRUCTIONS = """
You are an incident investigation agent for a small distributed system.

Investigate operational incidents using the available tools.

Rules:

- Never invent operational facts.
- Use tools to gather evidence.
- Check service dependencies when they may be relevant.
- Health status alone is not sufficient evidence that a request path works.
- Correlate logs, metrics, deployments and configuration where useful.
- Clearly distinguish facts from hypotheses.
- Do not claim a root cause unless evidence supports it.
- If evidence is insufficient, say so.
- Do not request or expose secrets.
- You have read-only access.
- Keep the final answer concise and evidence-based.
"""


def investigate(
    question: str,
    max_rounds: int = 8,
) -> str:
    provider = create_llm_provider()

    response = provider.start(
        question=question,
        instructions=INSTRUCTIONS,
        tools=TOOLS,
    )

    for _ in range(max_rounds):
        if not response.tool_calls:
            return response.text

        tool_results: list[ToolResult] = []

        for call in response.tool_calls:
            print()
            print(f"→ TOOL: {call.name}")
            print(
                json.dumps(
                    call.arguments,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            try:
                result = execute_tool(
                    call.name,
                    call.arguments,
                )
            except Exception as error:
                result = {
                    "error": error.__class__.__name__,
                    "message": str(error),
                }

            print()
            print("← RESULT")
            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            tool_results.append(
                ToolResult(
                    call=call,
                    output=result,
                )
            )

        response = provider.continue_with_tool_results(
            previous=response,
            tool_results=tool_results,
            instructions=INSTRUCTIONS,
            tools=TOOLS,
        )

    return (
        "Investigation stopped because the maximum "
        "number of tool rounds was reached."
    )
