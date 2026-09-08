from agentops_investigator.agent import investigate
from agentops_investigator.config import LLM_PROVIDER, get_llm_model


def main() -> None:
    print()
    print("AgentOps Incident Investigator")
    print(f"LLM: {LLM_PROVIDER} / {get_llm_model()}")
    print("Type 'exit' to quit.")
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
            answer = investigate(question)

            print()
            print("Agent:")
            print(answer)
            print()

        except Exception as error:
            print()
            print(
                f"Agent error: "
                f"{error.__class__.__name__}: {error}"
            )
            print()


if __name__ == "__main__":
    main()