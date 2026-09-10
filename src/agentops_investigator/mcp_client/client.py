from mcp import Client, StdioServerParameters

from agentops_investigator.config import LAB_DOCS_PATH, OPS_SERVICE_URL
from agentops_investigator.tools.definitions import ToolDefinition


def create_mcp_client() -> Client:
    """Create a local stdio MCP client for the AgentOps Lab server.

    The MCP subprocess receives only the configuration it needs.
    LLM provider credentials intentionally stay in the agent process.
    """
    server = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "python",
            "-m",
            "agentops_investigator.mcp_server.server",
        ],
        env={
            "OPS_SERVICE_URL": OPS_SERVICE_URL,
            "LAB_DOCS_PATH": str(LAB_DOCS_PATH),
        },
    )

    return Client(server)


async def load_mcp_tool_definitions(
    client: Client,
) -> list[ToolDefinition]:
    """Adapt MCP tool metadata to the provider-neutral LLM tool contract."""
    result = await client.list_tools()

    return [
        ToolDefinition(
            name=tool.name,
            description=tool.description or "",
            parameters=tool.input_schema,
        )
        for tool in result.tools
    ]
