import asyncio

from mcp import Client

from agentops_investigator.mcp_client.client import load_mcp_tool_definitions
from agentops_investigator.mcp_server.server import mcp

EXPECTED_MCP_TOOLS = {
    "list_services",
    "get_service_health",
    "get_service_metrics",
    "get_service_logs",
    "get_service_deployments",
    "get_service_config",
    "search_docs",
    "read_document",
}


def test_mcp_exposes_expected_tools_and_resource() -> None:
    async def run() -> None:
        async with Client(mcp) as client:
            tools_result = await client.list_tools()
            resources_result = await client.list_resources()

            assert {tool.name for tool in tools_result.tools} == EXPECTED_MCP_TOOLS
            assert {str(resource.uri) for resource in resources_result.resources} == {
                "docs://catalog"
            }

    asyncio.run(run())


def test_mcp_tool_metadata_adapts_to_llm_contract() -> None:
    async def run() -> None:
        async with Client(mcp) as client:
            definitions = await load_mcp_tool_definitions(client)

            assert {definition.name for definition in definitions} == EXPECTED_MCP_TOOLS
            assert all(
                definition.parameters.get("type") == "object"
                for definition in definitions
            )

    asyncio.run(run())
