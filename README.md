# AgentOps Incident Investigator

A small incident-investigation agent with provider-neutral tool calling.

## Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Put the API key for the provider you want to use into `.env`.

### Gemini

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
```

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-luna
```

No Python code needs to change when switching provider.

## Run

Make sure `ops-service` is running at the URL configured by `OPS_SERVICE_URL`, then:

```powershell
uv run agentops-investigator
```

## Architecture

```text
CLI
  -> agent.py                 provider-neutral orchestration
       -> llm/base.py         common LLM interface
       -> llm/factory.py      selects provider from LLM_PROVIDER
            -> GeminiProvider
            -> OpenAIProvider
       -> tools/              provider-neutral tools
       -> OpsClient           HTTP calls to ops-service
```

The agent owns the tool-execution loop. Each LLM provider only translates between the common internal representation and its provider-specific API.
