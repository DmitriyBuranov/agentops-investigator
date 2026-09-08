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
            "Use a trace_id to follow one request across services. "
            "Use level ERROR to discover failures. "
            "Health alone does not prove request paths work."
        ),
        parameters={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                },
                "level": {
                    "type": "string",
                    "description": (
                        "Optional log level such as ERROR or INFO."
                    ),
                },
                "trace_id": {
                    "type": "string",
                    "description": (
                        "Optional trace ID used to follow one "
                        "request across service boundaries."
                    ),
                },
            },
            "required": [
                "service",
            ],
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
    ToolDefinition(
        name="search_docs",
        description=(
            "Search the system documentation and runbooks. "
            "Use documentation to understand expected architecture, "
            "service contracts and investigation procedures. "
            "Documentation describes expected behavior and is not "
            "evidence of the current incident."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search query describing the operational "
                        "or architectural information needed."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": [
                "query",
            ],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="read_document",
        description=(
            "Read a Markdown document returned by search_docs. "
            "The path must be relative to the documentation root."
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
            },
            "required": [
                "path",
            ],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="complete_investigation",
        description=(
            "Finish an incident investigation with a structured report. "
            "Call this only after enough evidence has been collected "
            "or when the available evidence is insufficient."
        ),
        parameters={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "root_cause_identified",
                        "likely_cause",
                        "insufficient_evidence",
                    ],
                },
                "root_cause": {
                    "type": "string",
                },
                "confidence": {
                    "type": "string",
                    "enum": [
                        "low",
                        "medium",
                        "high",
                    ],
                },
                "affected_services": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "recommended_action": {
                    "type": "string",
                },
                "unknowns": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
            "required": [
                "status",
                "root_cause",
                "confidence",
                "affected_services",
                "evidence",
                "recommended_action",
                "unknowns",
            ],
            "additionalProperties": False,
        },
    ),
]
