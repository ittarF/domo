# === tools.py ===
import asyncio

def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny with 20\u00b0C."

TOOL_REGISTRY = {
    "get_weather": get_weather
}

async def execute_tool(name: str, params: dict) -> str:
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return f"Tool '{name}' not found."
    try:
        if asyncio.iscoroutinefunction(tool):
            return await tool(**params)
        return tool(**params)
    except Exception as e:
        return f"Error executing tool '{name}': {e}"
