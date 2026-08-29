import enum
from typing import Dict, Any
from app.ai.tools.base import BaseTool

class PermissionLevel(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"

def check_permission(tool: BaseTool, user_settings: Dict[str, Any]) -> bool:
    # Basic permission check implementation
    required_level = tool.permission_level
    user_level = user_settings.get("ai_permission_level", PermissionLevel.READ)
    
    levels = {
        PermissionLevel.READ: 1,
        PermissionLevel.WRITE: 2,
        PermissionLevel.EXECUTE: 3
    }
    
    return levels.get(user_level, 1) >= levels.get(required_level, 1)
