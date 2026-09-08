from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


TOOLS = [
    ToolDefinition(
        name="list_services",
        description=(
            "List services available in the operational system, "
            "including their versions and dependencies."
        ),
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="get_service_health",
        description=(
            "Get the current health status of a service. "
            "Health alone does not prove that all request paths work."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Exact service name.",
                },
            },
            "required": ["service"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="get_service_logs",
        description=(
            "Get recent structured logs for a service. "
            "Use level ERROR when investigating errors. "
            "Omit level when all log levels are needed."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                },
                "level": {
                    "type": "string",
                    "description": "Optional log level, for example ERROR or INFO.",
                },
            },
            "required": ["service"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="get_service_metrics",
        description=(
            "Get operational metrics for a service over a time window, "
            "including request count, error rate and latency."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                },
                "window_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1440,
                },
            },
            "required": ["service", "window_minutes"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="get_service_deployments",
        description=(
            "Get recent deployment history for a service. "
            "Useful for correlating failures with releases."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                },
            },
            "required": ["service"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="get_service_config",
        description=(
            "Get the safe operational configuration of a service. "
            "Secrets are redacted by ops-service."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                },
            },
            "required": ["service"],
            "additionalProperties": False,
        },
    ),
]
