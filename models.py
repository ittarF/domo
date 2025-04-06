from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]

class ResponseModel(BaseModel):
    response: str = Field(..., description="Natural language response")
    tool_call: Optional[ToolCall] = Field(None, description="Structured tool call if detected")

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
