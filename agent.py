from openrouter import get_openrouter_response
from parser import parse_response
from tools import execute_tool
from models import ResponseModel

class Agent:
    def __init__(self, model: str = "openrouter/quasar-alpha"):
        self.model = model

    def chat(self, user_input: str) -> ResponseModel:
        llm_output = get_openrouter_response(user_input, model=self.model)
        parsed = parse_response(llm_output)

        if parsed.tool_call:
            tool_result = execute_tool(parsed.tool_call.name, parsed.tool_call.parameters)
            parsed.response += f"\n\n🔧 Tool Result:\n{tool_result}"

        return parsed
