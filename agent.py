# === agent.py ===
from openrouter import get_openrouter_response
from parser import parse_response
from tools import execute_tool
from models import ResponseModel
from memory import Memory
from typing import Dict, List, Any, Optional
import logging
import httpx
import json

logger = logging.getLogger(__name__)

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
    def __init__(self, model: str = "openrouter/quasar-alpha", tool_manager_url: str = "http://localhost:8000"):
        self.model = model
        self.memory = Memory()
        self.tool_manager_url = tool_manager_url
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def _fetch_relevant_tools(self, prompt: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch tools relevant to the user prompt from the Tool Manager API.
        
        Args:
            prompt: User prompt
            top_k: Number of most relevant tools to return
            
        Returns:
            List of tool definitions
        """
        try:
            logger.debug(f"Fetching relevant tools for prompt: {prompt}")
            url = f"{self.tool_manager_url}/tool_lookup"
            
            response = await self.http_client.post(
                url,
                json={"prompt": prompt, "top_k": top_k}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Found {len(result.get('tools', []))} relevant tools")
            return result.get("tools", [])
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during tool lookup: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching relevant tools: {str(e)}")
            return []

    async def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call using the Tool Manager API.
        
        Args:
            tool_call: Tool call definition with name and parameters
            
        Returns:
            Tool execution result
        """
        try:
            logger.debug(f"Executing tool call: {tool_call}")
            url = f"{self.tool_manager_url}/tool_usage"
            
            # Convert tool_call to a serializable dictionary if it's not already
            if not isinstance(tool_call, dict):
                # If it's a Pydantic model or similar
                if hasattr(tool_call, "dict") and callable(tool_call.dict):
                    serializable_tool_call = tool_call.dict()
                # If it has a __dict__ attribute
                elif hasattr(tool_call, "__dict__"):
                    serializable_tool_call = tool_call.__dict__
                # Last resort - convert to string and parse as JSON if possible
                else:
                    try:
                        import json
                        serializable_tool_call = json.loads(json.dumps({"name": getattr(tool_call, "name", "unknown"), 
                                                                    "parameters": getattr(tool_call, "parameters", {})}))
                    except:
                        raise ValueError(f"Unable to serialize tool_call object: {type(tool_call)}")
            else:
                serializable_tool_call = tool_call
            
            response = await self.http_client.post(
                url,
                json={"tool_call": serializable_tool_call}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Tool execution result: {result}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during tool execution: {e.response.status_code} - {e.response.text}")
            return {"result": None, "error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {"result": None, "error": str(e)}


    async def build_context(self, user_input: str = None):
        if user_input:
            relevant_tools = await self._fetch_relevant_tools(user_input)
            
            # Format the tool descriptions for the model
            tools_context = "Available tools:\n"
            for tool in relevant_tools:
                tools_context += f"- {tool['name']}: {tool['description']}\n"
                tools_context += f"  Parameters: {json.dumps(tool['parameters'])}\n\n"
        else:
            tools_context = ""
        system_prompt = SYSTEM_MESSAGE + FORMATTING_INSTRUCTIONS + tools_context
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(self.memory.get_context_prompt())
        if user_input:
            messages.append({"role": "user", "content": user_input})
        return messages

    async def chat(self, user_input: str) -> ResponseModel:
        messages = await self.build_context(user_input)
        llm_output = await get_openrouter_response(messages, model=self.model)
        parsed = parse_response(llm_output)
        self.memory.add_user_message(user_input)
        self.memory.add_agent_message(parsed.response)

        if parsed.tool_call:
            try:
                # Execute the tool
                print('1')
                tool_result = await self._execute_tool(parsed.tool_call)
                print('2')
                # Convert the tool result to a safe string representation
                tool_result_str = json.dumps(tool_result, default=str)
                print('3')
                # Add the result to the response
                # parsed.response += f"\n\n🔧 Tool Result:\n{tool_result_str}"
                self.memory.add_agent_message(f"Tool Result\n{tool_result_str}")
            except Exception as e:
                error_message = f"Error processing tool result: {str(e)}"
                parsed.response += f"\n\n❌ Tool Error: {error_message}"
                self.memory.add_agent_message(f"Tool error: {error_message}")
            
            messages = await self.build_context()
            llm_output = await get_openrouter_response(messages, model=self.model)
            parsed = parse_response(llm_output)

                

        return parsed