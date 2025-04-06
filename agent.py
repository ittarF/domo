# === agent.py ===
from openrouter import get_openrouter_response
from parser import parse_response
from tools import execute_tool
from models import ResponseModel
from memory import Memory

SYSTEM_MESSAGE = (
    "You are an AI assistant with access to tools. "
    "Use these tools when appropriate to fulfill user requests. "
    "Always be helpful, accurate, and concise. "
    "IMPORTANT: You must remember all previously shared information within the conversation. "
    "If the user shares their name or preferences, remember this information for the duration of the conversation."
)

FORMATTING_INSTRUCTIONS = (
    "\nYou MUST format ALL your responses as valid JSON objects with this structure:\n"
    "```json\n"
    "{\n"
    "    \"response\": \"your helpful response text here\",\n"
    "    \"tool_call\": null\n"
    "}\n"
    "```\n"
    "When using a tool, set tool_call to a valid object like:\n"
    "```json\n"
    "{\n"
    "    \"response\": \"I'll check that for you\",\n"
    "    \"tool_call\": {\n"
    "        \"name\": \"tool_name\",\n"
    "        \"parameters\": {\n"
    "            \"param1\": \"value1\"\n"
    "        }\n"
    "    }\n"
    "}\n"
    "```\n"
    "ALWAYS respond in this JSON format. NEVER respond in plain text."
)

class Agent:
    def __init__(self, model: str = "openrouter/quasar-alpha"):
        self.model = model
        self.memory = Memory()

    def build_context(self, user_input: str):
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE + FORMATTING_INSTRUCTIONS}
        ]
        messages.extend(self.memory.get_context_prompt())
        messages.append({"role": "user", "content": user_input})
        return messages

    async def chat(self, user_input: str) -> ResponseModel:
        
        messages = self.build_context(user_input)
        print(f"INPUT: {messages}")
        llm_output = await get_openrouter_response(messages, model=self.model)
        parsed = parse_response(llm_output)
        self.memory.add_user_message(user_input)
        self.memory.add_agent_message(parsed.response)

        if parsed.tool_call:
            tool_result = await execute_tool(parsed.tool_call.name, parsed.tool_call.parameters)
            parsed.response += f"\n\n🔧 Tool Result:\n{tool_result}"
            self.memory.add_agent_message(f"Tool result: {tool_result}")

        return parsed
