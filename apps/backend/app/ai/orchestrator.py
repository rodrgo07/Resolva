from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.base import AIProvider
from app.ai.tools.base import BaseTool
from app.ai.permissions import check_permission
from app.models.ai import AIConversation, AIMessage
from app.schemas.ai import ChatResponse
from app.config import settings
from app.core.logging import logger

class AIOrchestrator:
    def __init__(self, db: AsyncSession, tools: Optional[List[BaseTool]] = None, services: Optional[Dict[str, Any]] = None):
        self.db = db
        if settings.AI_PROVIDER == "openai" and settings.AI_API_KEY:
            self.provider: AIProvider = OpenAIProvider(api_key=settings.AI_API_KEY, model=settings.AI_MODEL)
        else:
            self.provider: AIProvider = MockAIProvider()
            
        self.tools_map = {t.name: t for t in (tools or [])}
        self.services = services or {}

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

    async def process_message(self, user_message: str, conversation_id: Optional[int] = None) -> ChatResponse:
        # Load or create conversation
        if conversation_id:
            convo_res = await self.db.execute(select(AIConversation).where(AIConversation.id == conversation_id))
            conversation = convo_res.scalars().first()
            if not conversation:
                conversation = AIConversation(title=user_message[:40] + "...")
                self.db.add(conversation)
                await self.db.commit()
                await self.db.refresh(conversation)
        else:
            conversation = AIConversation(title=user_message[:40] + "...")
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

        # Save user message
        user_msg_db = AIMessage(
            conversation_id=conversation.id,
            role="user",
            content=user_message
        )
        self.db.add(user_msg_db)
        await self.db.commit()

        # Build history
        history_res = await self.db.execute(
            select(AIMessage).where(AIMessage.conversation_id == conversation.id).order_by(AIMessage.id.asc())
        )
        messages_db = history_res.scalars().all()
        messages = [{"role": m.role, "content": m.content} for m in messages_db]

        tools_schema = self._get_tools_schema()
        response = await self.provider.chat(messages, tools=tools_schema if tools_schema else None)

        tool_calls_made = []
        if response.tool_calls:
            for tc in response.tool_calls:
                tool_calls_made.append(tc.name)
                tool = self.tools_map.get(tc.name)
                if not tool:
                    result = {"error": f"Tool {tc.name} not found"}
                elif not check_permission(tool, {}):
                    result = {"error": f"Permission denied for tool {tc.name}"}
                else:
                    try:
                        result = await tool.execute(tc.arguments, self.services)
                    except Exception as e:
                        logger.error(f"Error executing tool {tc.name}: {str(e)}")
                        result = {"error": str(e)}

                messages.append({
                    "role": "tool",
                    "content": str(result)
                })

            # Call AI again with tool results
            final_response = await self.provider.chat(messages)
            reply_content = final_response.content or "Ação processada com sucesso."
        else:
            reply_content = response.content or "Olá! Como posso ajudar você hoje no Resolva?"

        # Save assistant message
        assistant_msg_db = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=reply_content,
            tool_calls=[tc.name for tc in response.tool_calls] if response.tool_calls else None
        )
        self.db.add(assistant_msg_db)
        await self.db.commit()

        return ChatResponse(
            message=reply_content,
            conversation_id=conversation.id,
            tool_calls_made=tool_calls_made
        )
