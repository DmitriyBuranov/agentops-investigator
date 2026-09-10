from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from agentops_investigator.llm.base import (
    LLMProvider,
    LLMResponse,
    ToolCall,
    ToolResult,
)
from agentops_investigator.tools.definitions import ToolDefinition


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str) -> None:
        self._model = model
        self._client = OpenAI()

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    def start(
        self,
        *,
        question: str,
        instructions: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        response = self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=question,
            tools=self._to_openai_tools(tools),
        )
        return self._parse_response(response)

    def continue_with_tool_results(
        self,
        *,
        previous: LLMResponse,
        tool_results: list[ToolResult],
        instructions: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        if not isinstance(previous.state, str):
            raise TypeError("OpenAI response state is missing the response id.")

        tool_outputs = [
            {
                "type": "function_call_output",
                "call_id": result.call.id,
                "output": json.dumps(result.output, ensure_ascii=False),
            }
            for result in tool_results
        ]

        response = self._client.responses.create(
            model=self._model,
            instructions=instructions,
            previous_response_id=previous.state,
            input=tool_outputs,
            tools=self._to_openai_tools(tools),
        )
        return self._parse_response(response)

    @staticmethod
    def _to_openai_tools(
        tools: list[ToolDefinition],
    ) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in tools
        ]

    @staticmethod
    def _parse_response(response: Any) -> LLMResponse:
        tool_calls: list[ToolCall] = []

        for item in response.output:
            if item.type != "function_call":
                continue

            tool_calls.append(
                ToolCall(
                    id=item.call_id,
                    name=item.name,
                    arguments=json.loads(item.arguments),
                )
            )

        return LLMResponse(
            text=response.output_text or "",
            tool_calls=tool_calls,
            state=response.id,
        )
