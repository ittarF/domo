def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny with 20°C."

TOOL_REGISTRY = {
    "get_weather": get_weather,
}

def execute_tool(name: str, params: dict) -> str:
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return f"Tool '{name}' not found."
    try:
        return tool(**params)
    except Exception as e:
        return f"Error executing tool '{name}': {e}"
