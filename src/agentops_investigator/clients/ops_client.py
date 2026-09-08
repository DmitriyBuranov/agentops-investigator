from typing import Any

import httpx

from agentops_investigator.config import OPS_SERVICE_URL


class OpsClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=OPS_SERVICE_URL,
            timeout=5.0,
        )

    def list_services(self) -> list[dict[str, Any]]:
        response = self._client.get("/services")
        response.raise_for_status()

        return response.json()

    def get_health(
        self,
        service: str,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/services/{service}/health"
        )
        response.raise_for_status()

        return response.json()

    def get_logs(
        self,
        service: str,
        level: str | None = None,
        trace_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "limit": limit,
        }

        if level is not None:
            params["level"] = level

        if trace_id is not None:
            params["trace_id"] = trace_id

        response = self._client.get(
            f"/services/{service}/logs",
            params=params,
        )

        response.raise_for_status()

        return response.json()

    def get_metrics(
        self,
        service: str,
        window_minutes: int = 15,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/services/{service}/metrics",
            params={
                "window_minutes": window_minutes,
            },
        )
        response.raise_for_status()

        return response.json()

    def get_deployments(
        self,
        service: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/services/{service}/deployments",
            params={
                "limit": limit,
            },
        )
        response.raise_for_status()

        return response.json()

    def get_config(
        self,
        service: str,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/services/{service}/config"
        )
        response.raise_for_status()

        return response.json()