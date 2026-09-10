from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from agentops_investigator.config import LAB_DOCS_PATH
from agentops_investigator.tools.operations import (
    get_service_config as get_service_config_impl,
)
from agentops_investigator.tools.operations import (
    get_service_deployments as get_service_deployments_impl,
)
from agentops_investigator.tools.operations import (
    get_service_health as get_service_health_impl,
)
from agentops_investigator.tools.operations import (
    get_service_logs as get_service_logs_impl,
)
from agentops_investigator.tools.operations import (
    get_service_metrics as get_service_metrics_impl,
)
from agentops_investigator.tools.operations import (
    list_services as list_services_impl,
)
from agentops_investigator.tools.operations import (
    read_document as read_document_impl,
)
from agentops_investigator.tools.operations import (
    search_docs as search_docs_impl,
)

mcp = MCPServer(
    "AgentOps Lab",
    instructions=(
        "Provides read-only operational and documentation "
        "access to the Agent Incident Lab."
    ),
)

READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    open_world_hint=False,
)


@mcp.tool(annotations=READ_ONLY)
def list_services() -> list[dict[str, Any]]:
    """List all services available in the operational system."""
    return list_services_impl()


@mcp.tool(annotations=READ_ONLY)
def get_service_health(
    service: str,
) -> dict[str, Any]:
    """Get the current health status of a service."""
    return get_service_health_impl(service=service)


@mcp.tool(annotations=READ_ONLY)
def get_service_metrics(
    service: str,
    window_minutes: int = 15,
) -> dict[str, Any]:
    """Get request, error-rate and latency metrics for a service."""
    return get_service_metrics_impl(
        service=service,
        window_minutes=window_minutes,
    )


@mcp.tool(annotations=READ_ONLY)
def get_service_logs(
    service: str,
    level: str | None = None,
    trace_id: str | None = None,
) -> list[dict[str, Any]]:
    """Get recent structured logs; trace_id can follow one request."""
    return get_service_logs_impl(
        service=service,
        level=level,
        trace_id=trace_id,
    )


@mcp.tool(annotations=READ_ONLY)
def get_service_deployments(
    service: str,
) -> list[dict[str, Any]]:
    """Get recent deployment history for a service."""
    return get_service_deployments_impl(service=service)


@mcp.tool(annotations=READ_ONLY)
def get_service_config(
    service: str,
) -> dict[str, Any]:
    """Get safe runtime configuration; secrets remain redacted."""
    return get_service_config_impl(service=service)


@mcp.tool(annotations=READ_ONLY)
def search_docs(
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Search architecture docs and runbooks for expected behavior."""
    return search_docs_impl(
        query=query,
        limit=limit,
    )


@mcp.tool(annotations=READ_ONLY)
def read_document(
    path: str,
) -> dict[str, Any]:
    """Read one Markdown document from the allowed documentation root."""
    return read_document_impl(path=path)


@mcp.resource("docs://catalog")
def documentation_catalog() -> str:
    """List Markdown documents exposed by the lab documentation root."""
    documents = [
        path.relative_to(LAB_DOCS_PATH).as_posix()
        for path in LAB_DOCS_PATH.rglob("*.md")
    ]

    return "\n".join(sorted(documents))


if __name__ == "__main__":
    mcp.run()
