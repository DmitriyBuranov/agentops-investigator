import json
from typing import Any

from mcp import Client
from mcp.types import TextContent

from agentops_investigator.llm import ToolResult, create_llm_provider
from agentops_investigator.mcp_client.client import load_mcp_tool_definitions
from agentops_investigator.tools.definitions import COMPLETE_INVESTIGATION_TOOL

INSTRUCTIONS = """
You are an operations and incident investigation agent
for a small distributed system.

Your goal is not merely to find suspicious data.
Your goal is to determine the most defensible explanation
for an incident from the available evidence.

Use the minimum number of tools necessary.

OPERATIONAL EVIDENCE

Health, metrics, logs, configuration and deployment history
describe the current or observed state of the system.

Use them as evidence.

DOCUMENTATION

Documentation describes expected architecture, contracts,
timeouts, dependencies and operational procedures.

Documentation can guide an investigation, but documentation
is NOT evidence that a particular incident currently exists.

If documentation conflicts with observed operational data,
explicitly mention the discrepancy and prefer operational evidence.

INVESTIGATION

For simple status questions:
- Prefer health and metrics.
- Do not perform a full incident investigation unnecessarily.

For incident or root-cause questions:

1. Identify the affected service or request path.
2. Inspect relevant operational evidence.
3. Inspect dependencies when relevant.
4. When a failed request has a trace ID, follow that trace across
   relevant services when it can help establish causality.
5. Use documentation when you need to understand expected
   architecture, contracts, timeouts or investigation procedures.
6. Check deployments when a recent code change may explain
   observed behavior.
7. Check configuration when configuration or compatibility may
   explain observed behavior.
8. Test competing explanations where possible.
9. Stop once enough evidence exists.

REASONING RULES

- Never invent operational facts.
- Health status alone does not prove that business requests work.
- Correlation with a deployment is evidence, but not automatically proof.
- Clearly distinguish observation from hypothesis.
- Do not claim a root cause unless evidence supports it.
- If multiple explanations remain plausible, say so.
- If evidence is insufficient, explicitly report that.
- Never request or expose secrets.
- Treat redacted values as intentionally unavailable.
- You have read-only access.

For an incident investigation, finish by calling
complete_investigation.

Do not call complete_investigation until the investigation
has enough evidence or you have established that the evidence
is insufficient.

Do not combine complete_investigation with other tool calls
in the same response.
"""


def extract_text(result: Any) -> str:
    """Extract model-readable text blocks from an MCP tool result."""
    return "\n".join(
        block.text for block in result.content if isinstance(block, TextContent)
    )


async def execute_mcp_tool(
    mcp_client: Client,
    name: str,
    arguments: dict[str, Any],
) -> Any:
    """Execute one MCP tool and return a provider-neutral result."""
    result = await mcp_client.call_tool(
        name,
        arguments,
    )

    if result.is_error:
        return {
            "error": "MCPToolError",
            "message": extract_text(result),
        }

    if result.structured_content is not None:
        return result.structured_content

    return extract_text(result)


async def investigate(
    mcp_client: Client,
    question: str,
    max_rounds: int = 8,
    max_tool_calls: int = 20,
) -> str:
    provider = create_llm_provider()

    mcp_tools = await load_mcp_tool_definitions(mcp_client)
    tools = [
        *mcp_tools,
        COMPLETE_INVESTIGATION_TOOL,
    ]

    response = provider.start(
        question=question,
        instructions=INSTRUCTIONS,
        tools=tools,
    )

    tool_call_count = 0
    seen_calls: set[str] = set()

    for _ in range(max_rounds):
        if not response.tool_calls:
            return response.text

        completion_calls = [
            call
            for call in response.tool_calls
            if call.name == COMPLETE_INVESTIGATION_TOOL.name
        ]

        if completion_calls:
            if len(response.tool_calls) != 1:
                return (
                    "Agent attempted to complete the investigation "
                    "while also requesting additional tools."
                )

            return format_investigation_report(completion_calls[0].arguments)

        tool_results: list[ToolResult] = []

        for call in response.tool_calls:
            tool_call_count += 1

            if tool_call_count > max_tool_calls:
                return (
                    "Investigation stopped because "
                    "the maximum number of tool calls was reached."
                )

            print()
            print(f"→ TOOL: {call.name}")
            print(
                json.dumps(
                    call.arguments,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            # Temporary read-only optimization. Revisit once write actions
            # (for example rollback) can intentionally change system state.
            fingerprint = json.dumps(
                {
                    "name": call.name,
                    "arguments": call.arguments,
                },
                sort_keys=True,
                ensure_ascii=False,
            )

            if fingerprint in seen_calls:
                print("⚠ Duplicate tool call blocked")
                result = {
                    "error": "DuplicateToolCall",
                    "message": (
                        "This exact tool call has already been "
                        "executed during this investigation. "
                        "Use the previous observation or call "
                        "a different tool."
                    ),
                }
            else:
                seen_calls.add(fingerprint)

                try:
                    result = await execute_mcp_tool(
                        mcp_client=mcp_client,
                        name=call.name,
                        arguments=call.arguments,
                    )
                except Exception as error: # noqa: BLE001 - tool boundary must isolate arbitrary tool failures
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
            tools=tools,
        )

    return (
        "Investigation stopped because the maximum number of tool rounds was reached."
    )


def format_investigation_report(
    data: dict[str, Any],
) -> str:
    lines = [
        f"Status: {data['status']}",
        f"Confidence: {data['confidence']}",
        "",
        "Root cause:",
        data["root_cause"],
        "",
        "Affected services:",
    ]

    for service in data["affected_services"]:
        lines.append(f"- {service}")

    lines.extend(["", "Evidence:"])

    for evidence in data["evidence"]:
        lines.append(f"- {evidence}")

    lines.extend(
        [
            "",
            "Recommended action:",
            data["recommended_action"],
        ]
    )

    if data["unknowns"]:
        lines.extend(["", "Unknowns:"])

        for unknown in data["unknowns"]:
            lines.append(f"- {unknown}")

    return "\n".join(lines)
