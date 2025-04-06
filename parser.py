import json
import re
from models import ResponseModel, ToolCall

def parse_response(llm_output: str) -> ResponseModel:
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", llm_output, re.DOTALL)
    if match:
        try:
            tool_call_data = json.loads(match.group(1))
            tool_call = ToolCall(**tool_call_data)
            response_text = re.sub(r"```(?:json)?\s*{.*?}\s*```", "", llm_output, flags=re.DOTALL).strip()
            return ResponseModel(response=response_text, tool_call=tool_call)
        except (json.JSONDecodeError, ValueError):
            pass
    return ResponseModel(response=llm_output.strip())
