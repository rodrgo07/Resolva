import re
from typing import Tuple, Dict, Any

ALLOWED_COMMANDS = [
    "create_task", "update_task", "complete_task",
    "create_expense", "send_notification"
]

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"drop\s+table",
    r"delete\s+from\s+users"
]

def validate_command(cmd: str) -> bool:
    if cmd not in ALLOWED_COMMANDS:
        return False
    return True

def check_action_safety(action: Dict[str, Any]) -> Tuple[bool, str]:
    action_type = action.get("type", "")
    
    if not validate_command(action_type):
        return False, f"Action type '{action_type}' is not in the allowed commands list."
        
    config_str = str(action.get("config", {})).lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, config_str):
            return False, f"Dangerous pattern detected in action configuration."
            
    return True, "Action is safe."
