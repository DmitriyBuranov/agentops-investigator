from typing import Any

from agentops_investigator.clients.ops_client import OpsClient
from agentops_investigator.config import LAB_DOCS_PATH
from agentops_investigator.knowledge.store import KnowledgeStore

_ops = OpsClient()


def list_services() -> list[dict[str, Any]]:
    return _ops.list_services()


def get_service_health(
    service: str,
) -> dict[str, Any]:
    return _ops.get_health(service)


def get_service_logs(
    service: str,
    level: str | None = None,
    trace_id: str | None = None,
) -> list[dict[str, Any]]:
    return _ops.get_logs(
        service=service,
        level=level,
        trace_id=trace_id,
        limit=100,
    )


def get_service_metrics(
    service: str,
    window_minutes: int,
) -> dict[str, Any]:
    return _ops.get_metrics(
        service=service,
        window_minutes=window_minutes,
    )


def get_service_deployments(
    service: str,
) -> list[dict[str, Any]]:
    return _ops.get_deployments(
        service=service,
        limit=20,
    )


def get_service_config(
    service: str,
) -> dict[str, Any]:
    return _ops.get_config(service)


_knowledge = KnowledgeStore(LAB_DOCS_PATH)


def search_docs(
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    return _knowledge.search(
        query=query,
        limit=limit,
    )


def read_document(
    path: str,
) -> dict[str, Any]:
    return _knowledge.read_document(
        relative_path=path,
    )
