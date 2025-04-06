from openrouter import get_openrouter_response
from parser import parse_response
from tools import execute_tool
from models import ResponseModel
from memory import Memory

class Agent:
    def __init__(self, model: str = "openrouter/quasar-alpha"):
        self.model = model
        self.memory = Memory()

    async def chat(self, user_input: str) -> ResponseModel:
        self.memory.add_user_message(user_input)

        llm_output = await get_openrouter_response(
            self.memory.get_context_prompt(),
            model=self.model
        )

        parsed = parse_response(llm_output)
        self.memory.add_agent_message(parsed.response)

        if parsed.tool_call:
            tool_result = await execute_tool(parsed.tool_call.name, parsed.tool_call.parameters)
            parsed.response += f"\n\n🔧 Tool Result:\n{tool_result}"
            self.memory.add_agent_message(f"Tool result: {tool_result}")

        return parsed