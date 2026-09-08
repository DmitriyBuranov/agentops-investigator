import os

from dotenv import load_dotenv

from pathlib import Path


load_dotenv()


OPS_SERVICE_URL = os.getenv(
    "OPS_SERVICE_URL",
    "http://localhost:8003",
)

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "gemini",
).strip().lower()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

LAB_DOCS_PATH = Path(
    os.getenv(
        "LAB_DOCS_PATH",
        "../agent-incident-lab/docs",
    )
).resolve()


def get_llm_model() -> str:
    if LLM_PROVIDER == "gemini":
        return GEMINI_MODEL
    if LLM_PROVIDER == "openai":
        return OPENAI_MODEL
    return "unknown"
