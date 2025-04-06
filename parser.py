# === parser.py ===
import json
import re
from models import ResponseModel, ToolCall

def parse_response(llm_output: str) -> ResponseModel:
    # Estrai il JSON tra i backtick, se presenti
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", llm_output, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # fallback: usa tutto il testo se non ci sono backtick
        json_str = llm_output.strip()

    try:
        data = json.loads(json_str)

        # tool_call può essere null, quindi gestiamo i casi
        tool_call_data = data.get("tool_call")
        tool_call = ToolCall(**tool_call_data) if tool_call_data else None

        return ResponseModel(response=data.get("response", "").strip(), tool_call=tool_call)

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        raise ValueError(f"❌ Failed to parse response: {e}\n--- Content ---\n{llm_output}")
