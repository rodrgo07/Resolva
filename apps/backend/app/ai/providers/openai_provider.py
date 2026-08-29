import httpx
from typing import List, Dict, Any, Optional
import json
from app.ai.providers.base import AIProvider, AIResponse, ToolCall
from app.config import settings
from app.core.logging import logger

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> AIResponse:
        if not self.api_key:
            logger.warning("OpenAI API key not found, using fallback")
            return AIResponse(content="OpenAI API key not configured.", tool_calls=None, usage={})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.AI_TEMPERATURE,
            "max_tokens": settings.AI_MAX_TOKENS
        }
        
        if tools:
            payload["tools"] = tools

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                message = data["choices"][0]["message"]
                content = message.get("content")
                
                tool_calls = None
                if "tool_calls" in message:
                    tool_calls = []
                    for tc in message["tool_calls"]:
                        if tc["type"] == "function":
                            args_str = tc["function"]["arguments"]
                            try:
                                args = json.loads(args_str)
                            except:
                                args = {}
                            tool_calls.append(ToolCall(
                                id=tc["id"],
                                name=tc["function"]["name"],
                                arguments=args
                            ))
                            
                usage = data.get("usage", {})
                return AIResponse(content=content, tool_calls=tool_calls, usage=usage)
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            return AIResponse(content=f"Error processing AI request: {str(e)}", tool_calls=None, usage={})
