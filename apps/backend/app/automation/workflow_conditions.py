from typing import Dict, Any, List, Union
from enum import Enum
from app.core.logging import logger

class ConditionOperator(str, Enum):
    EQ = "EQ"
    NEQ = "NEQ"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    IN = "IN"
    NOT_IN = "NOT_IN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    IS_EMPTY = "IS_EMPTY"
    IS_NOT_EMPTY = "IS_NOT_EMPTY"

class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class WorkflowConditionsEngine:
    """
    Avaliador determinístico e seguro de condições para Workflows.
    NUNCA utiliza eval(), exec() ou compilação dinâmica de código.
    Avalia estritamente estruturas declarativas de dados contra o contexto sanitizado.
    """

    @staticmethod
    def evaluate_condition(condition_config: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if not condition_config:
            return True

        # Suporta operadores lógicos no nível superior (AND, OR, NOT)
        if "AND" in condition_config:
            sub_conds = condition_config["AND"]
            if not isinstance(sub_conds, list):
                return False
            return all(WorkflowConditionsEngine.evaluate_condition(c, context) for c in sub_conds)

        if "OR" in condition_config:
            sub_conds = condition_config["OR"]
            if not isinstance(sub_conds, list):
                return False
            return any(WorkflowConditionsEngine.evaluate_condition(c, context) for c in sub_conds)

        if "NOT" in condition_config:
            sub_cond = condition_config["NOT"]
            return not WorkflowConditionsEngine.evaluate_condition(sub_cond, context)

        # Condição de campo único
        field = condition_config.get("field")
        op = condition_config.get("operator", "EQ").upper()
        target_value = condition_config.get("value")

        if not field:
            return True

        actual_value = WorkflowConditionsEngine._extract_nested_field(field, context)
        return WorkflowConditionsEngine._compare(actual_value, op, target_value)

    @staticmethod
    def _extract_nested_field(field_path: str, context: Dict[str, Any]) -> Any:
        parts = field_path.split(".")
        curr: Any = context
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                return None
        return curr

    @staticmethod
    def _compare(actual: Any, op: str, target: Any) -> bool:
        try:
            if op == ConditionOperator.EQ.value:
                return actual == target
            elif op == ConditionOperator.NEQ.value:
                return actual != target
            elif op == ConditionOperator.GT.value:
                return actual is not None and target is not None and float(actual) > float(target)
            elif op == ConditionOperator.GTE.value:
                return actual is not None and target is not None and float(actual) >= float(target)
            elif op == ConditionOperator.LT.value:
                return actual is not None and target is not None and float(actual) < float(target)
            elif op == ConditionOperator.LTE.value:
                return actual is not None and target is not None and float(actual) <= float(target)
            elif op == ConditionOperator.IN.value:
                return target is not None and actual in target
            elif op == ConditionOperator.NOT_IN.value:
                return target is not None and actual not in target
            elif op == ConditionOperator.CONTAINS.value:
                if isinstance(actual, (str, list, dict)):
                    return target in actual
                return False
            elif op == ConditionOperator.NOT_CONTAINS.value:
                if isinstance(actual, (str, list, dict)):
                    return target not in actual
                return True
            elif op == ConditionOperator.IS_EMPTY.value:
                if actual is None:
                    return True
                if isinstance(actual, (str, list, dict)):
                    return len(actual) == 0
                return False
            elif op == ConditionOperator.IS_NOT_EMPTY.value:
                if actual is None:
                    return False
                if isinstance(actual, (str, list, dict)):
                    return len(actual) > 0
                return True
            else:
                logger.warning(f"Operador desconhecido em condição de workflow: {op}")
                return False
        except Exception as e:
            logger.error(f"Erro ao comparar condição ({actual} {op} {target}): {e}")
            return False
