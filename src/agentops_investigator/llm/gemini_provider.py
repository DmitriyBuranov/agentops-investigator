from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types

from agentops_investigator.llm.base import (
    LLMProvider,
    LLMResponse,
    ToolCall,
    ToolResult,
)
from agentops_investigator.tools.definitions import ToolDefinition


@dataclass
class _GeminiState:
    contents: list[Any]


class GeminiProvider(LLMProvider):
    def __init__(self, model: str) -> None:
        self._model = model
        self._client = genai.Client()

    @property
    def name(self) -> str:
        return "gemini"

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
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=question)],
            )
        ]

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=self._build_config(instructions, tools),
        )
        return self._parse_response(response, contents)

    def continue_with_tool_results(
        self,
        *,
        previous: LLMResponse,
        tool_results: list[ToolResult],
        instructions: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        if not isinstance(previous.state, _GeminiState):
            raise ValueError("Gemini response state is missing conversation history.")

        function_responses = []

        for result in tool_results:
            function_response_kwargs: dict[str, Any] = {
                "name": result.call.name,
                "response": {
                    "result": result.output,
                },
            }

            if result.call.id:
                function_response_kwargs["id"] = result.call.id

            function_response = types.FunctionResponse(
                **function_response_kwargs
            )

            function_responses.append(
                types.Part(
                    function_response=function_response
                )
            )

        contents = [
            *previous.state.contents,
            types.Content(
                role="user",
                parts=function_responses,
            ),
        ]

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=self._build_config(instructions, tools),
        )
        return self._parse_response(response, contents)

    @staticmethod
    def _build_config(
        instructions: str,
        tools: list[ToolDefinition],
    ) -> types.GenerateContentConfig:
        function_declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=GeminiProvider._to_gemini_schema(tool.parameters),
            )
            for tool in tools
        ]

        return types.GenerateContentConfig(
            system_instruction=instructions,
            tools=[
                types.Tool(
                    function_declarations=function_declarations,
                )
            ],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

    @staticmethod
    def _to_gemini_schema(value: Any) -> Any:
        # Gemini supports a JSON Schema subset. Provider-neutral definitions
        # may contain keywords used by other providers, so strip those here.
        if isinstance(value, dict):
            return {
                key: GeminiProvider._to_gemini_schema(item)
                for key, item in value.items()
                if key != "additionalProperties"
            }
        if isinstance(value, list):
            return [GeminiProvider._to_gemini_schema(item) for item in value]
        return value

    @staticmethod
    def _parse_response(
        response: Any,
        input_contents: list[Any],
    ) -> LLMResponse:
        if not response.candidates:
            return LLMResponse(text="", state=_GeminiState(input_contents))

        model_content = response.candidates[0].content
        tool_calls: list[ToolCall] = []
        text_parts: list[str] = []

        for part in model_content.parts or []:
            text = getattr(part, "text", None)
            if text:
                text_parts.append(text)

            function_call = getattr(part, "function_call", None)
            if function_call is None:
                continue

            tool_calls.append(
                ToolCall(
                    id=getattr(function_call, "id", None),
                    name=function_call.name,
                    arguments=dict(function_call.args or {}),
                )
            )

        return LLMResponse(
            text="".join(text_parts),
            tool_calls=tool_calls,
            state=_GeminiState(
                contents=[*input_contents, model_content]
            ),
        )
