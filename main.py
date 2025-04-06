# === main.py ===
import asyncio
from agent import Agent

async def main():
    print("\n🤖 Agent Chat (async + memory) — type 'exit' to quit")
    agent = Agent()

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            result = await agent.chat(user_input)
            print(f"\n🧠 Agent: {result.response}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())