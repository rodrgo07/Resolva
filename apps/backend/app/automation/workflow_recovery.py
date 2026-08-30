from typing import Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime

class WorkflowRecoveryEngine:
    """
    Motor de Resiliência e Recuperação Segura de Workflows (Fase 34).
    Lida com classificação de erros, backoff exponencial e nunca repete ações de alto risco sem confirmação.
    """

    MAX_RETRIES = 3
    BASE_BACKOFF_SECONDS = 2

    @classmethod
    def classify_error(cls, error: Any) -> Tuple[str, bool]:
        """
        Classifica o erro e define se é recuperável de forma segura.
        Retorna (ErrorCategory, IsRetryable).
        """
        err_str = str(error).lower()

        if "timeout" in err_str or "timed out" in err_str:
            return "TRANSIENT_TIMEOUT", True
        elif "connection" in err_str or "network" in err_str or "locked" in err_str:
            return "CONCURRENCY_OR_LOCK", True
        elif "permission" in err_str or "forbidden" in err_str or "proibido" in err_str:
            return "PERMISSION_DENIED", False
        elif "not found" in err_str or "não encontrado" in err_str:
            return "RESOURCE_NOT_FOUND", False
        elif "validation" in err_str or "inválido" in err_str:
            return "VALIDATION_FAILURE", False
        else:
            return "UNCLASSIFIED_ERROR", False

    @classmethod
    async def execute_with_recovery(
        cls,
        action_coroutine_fn,
        step_name: str,
        permission_level: str,
        max_attempts: int = 2
    ) -> Tuple[bool, Dict[str, Any], int]:
        """
        Executa a função de etapa com política de retry seguro.
        """
        attempts = 0
        last_error = None

        while attempts < max(1, min(cls.MAX_RETRIES, max_attempts)):
            attempts += 1
            try:
                ok, result = await action_coroutine_fn()
                if ok:
                    return True, result, attempts
                else:
                    last_error = result
            except Exception as ex:
                last_error = str(ex)

            cat, retryable = cls.classify_error(last_error)

            # Ações de risco Médio/Alto NUNCA sofrem retry automático se falharem por permissão ou validação
            if not retryable or permission_level in ["MEDIUM", "HIGH"]:
                break

            if attempts < max_attempts:
                backoff = cls.BASE_BACKOFF_SECONDS * (2 ** (attempts - 1))
                await asyncio.sleep(min(backoff, 10))

        return False, {"error": f"Falha após {attempts} tentativa(s): {last_error}"}, attempts
