from typing import List, Dict, Any
from app.automation.security import check_action_safety
from app.automation.actions.base import ActionResult, BaseAction
from app.core.logging import logger

class AutomationEngine:
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        # Map of action types to Action classes would go here
        self.action_registry = {}

    def validate_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        invalid_actions = []
        for action in actions:
            is_safe, reason = check_action_safety(action)
            if not is_safe:
                invalid_actions.append({"action": action.get("type"), "reason": reason})
        return invalid_actions

    async def execute_sequentially(self, actions_config: List[Dict[str, Any]]) -> List[ActionResult]:
        results = []
        
        invalid = self.validate_actions(actions_config)
        if invalid:
            logger.error(f"Automation execution aborted due to invalid actions: {invalid}")
            return [ActionResult(success=False, message="Validation failed", error=str(invalid))]
            
        for config in actions_config:
            action_type = config.get("type")
            ActionClass = self.action_registry.get(action_type)
            
            if not ActionClass:
                err_res = ActionResult(success=False, message=f"Action '{action_type}' not found")
                results.append(err_res)
                logger.error(err_res.message)
                break # Stop on error by default
                
            try:
                action_instance = ActionClass(
                    type=action_type, 
                    config=config.get("config", {}),
                    requires_confirmation=config.get("requires_confirmation", False)
                )
                
                # Mock execution for now as no concrete actions are defined yet
                logger.info(f"Executing action: {action_type}")
                result = ActionResult(success=True, message=f"Executed {action_type}") 
                # result = await action_instance.execute()
                
                results.append(result)
                if not result.success:
                    logger.error(f"Action {action_type} failed: {result.error}")
                    break
                    
            except Exception as e:
                err_res = ActionResult(success=False, message=f"Exception in '{action_type}'", error=str(e))
                results.append(err_res)
                logger.error(err_res.message)
                break
                
        return results
