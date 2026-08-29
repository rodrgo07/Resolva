from typing import List, Dict, Any, Optional
from app.ai.providers.base import AIProvider
from app.ai.tools.base import BaseTool
from app.ai.permissions import check_permission
from app.core.logging import logger

class AIOrchestrator:
    def __init__(self, provider: AIProvider, tools: List[BaseTool], services: Dict[str, Any]):
        self.provider = provider
        self.tools_map = {t.name: t for t in tools}
        self.services = services

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        schemas = []
        for tool in self.tools_map.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas

    async def process_message(self, user_message: str, history: List[Dict[str, Any]], user_settings: Dict[str, Any]) -> str:
        messages = history + [{"role": "user", "content": user_message}]
        tools_schema = self._get_tools_schema()
        
        # Initial call
        response = await self.provider.chat(messages, tools=tools_schema)
        
        # If no tool calls, return content directly
        if not response.tool_calls:
            return response.content or "No response from AI."
            
        # Process tool calls
        messages.append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": str(tc.arguments)}
                } for tc in response.tool_calls
            ]
        })
        
        for tc in response.tool_calls:
            tool = self.tools_map.get(tc.name)
            if not tool:
                result = {"error": f"Tool {tc.name} not found"}
            elif not check_permission(tool, user_settings):
                result = {"error": f"Permission denied for tool {tc.name}"}
            else:
                try:
                    result = await tool.execute(tc.arguments, self.services)
                except Exception as e:
                    logger.error(f"Error executing tool {tc.name}: {str(e)}")
                    result = {"error": str(e)}
                    
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.name,
                "content": str(result)
            })
            
        # Final call to summarize tool results
        final_response = await self.provider.chat(messages)
        return final_response.content or "Task completed based on tool results."
