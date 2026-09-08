from typing import Any

from agentops_investigator.clients.ops_client import OpsClient


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
) -> list[dict[str, Any]]:
    return _ops.get_logs(
        service=service,
        level=level,
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