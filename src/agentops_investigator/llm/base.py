from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentops_investigator.tools.definitions import ToolDefinition


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str | None = None


@dataclass(frozen=True)
class ToolResult:
    call: ToolCall
    output: Any


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    state: Any = field(default=None, repr=False)


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def start(
        self,
        *,
        question: str,
        instructions: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    def continue_with_tool_results(
        self,
        *,
        previous: LLMResponse,
        tool_results: list[ToolResult],
        instructions: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        raise NotImplementedError
