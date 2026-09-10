import asyncio

from agentops_investigator.agent import investigate
from agentops_investigator.config import LLM_PROVIDER, get_llm_model
from agentops_investigator.mcp_client.client import create_mcp_client


async def async_main() -> None:
    print()
    print("AgentOps Incident Investigator")
    print(f"LLM: {LLM_PROVIDER} / {get_llm_model()}")
    print("Type 'exit' to quit.")
    print()

    async with create_mcp_client() as mcp_client:
        tools = await mcp_client.list_tools()

        server_name = (
            mcp_client.server_info.name
            if mcp_client.server_info is not None
            else "unknown"
        )

        print(
            f"MCP: {server_name} | "
            f"protocol={mcp_client.protocol_version} | "
            f"tools={len(tools.tools)}"
        )
        print()

        while True:
            question = input("You: ").strip()

            if question.lower() in {
                "exit",
                "quit",
            }:
                break

            if not question:
                continue

            try:
                answer = await investigate(
                    mcp_client=mcp_client,
                    question=question,
                )
            except Exception as error: # noqa: BLE001 - CLI is the top-level error boundary
                print()
                print(f"Agent error: {error.__class__.__name__}: {error}")
                print()
                continue

            print()
            print("Agent:")
            print(answer)
            print()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
