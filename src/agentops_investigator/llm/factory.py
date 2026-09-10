from agentops_investigator.config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENAI_MODEL,
)
from agentops_investigator.llm.base import LLMProvider


def create_llm_provider() -> LLMProvider:
    if LLM_PROVIDER == "gemini":
        from agentops_investigator.llm.gemini_provider import GeminiProvider

        return GeminiProvider(model=GEMINI_MODEL)

    if LLM_PROVIDER == "openai":
        from agentops_investigator.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(model=OPENAI_MODEL)

    raise ValueError(
        f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. Supported values: gemini, openai."
    )
