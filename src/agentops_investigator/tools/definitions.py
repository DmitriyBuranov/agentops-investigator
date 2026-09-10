from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


COMPLETE_INVESTIGATION_TOOL = ToolDefinition(
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
)
