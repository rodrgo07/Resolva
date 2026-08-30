from enum import Enum
from typing import Dict, Any, Optional

class PermissionLevel(str, Enum):
    READ = "READ"           # Consultas e leituras sem efeitos colaterais
    SUGGEST = "SUGGEST"     # Geração de planos, análises e sugestões
    PREPARE = "PREPARE"     # Preparação de ações (draft de e-mail, plano do dia)
    CONFIRM = "CONFIRM"     # Requer confirmação explícita do usuário
    WRITE = "WRITE"         # Escrita após confirmação
    EXECUTE = "EXECUTE"     # Execução de automações ou ações de alto impacto

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

def check_permission(tool: Any, user_context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Verifica se a Tool possui permissão para execução.
    Se a tool requer confirmação (risk medium/high ou write/execute), valida se a confirmação explícita foi fornecida.
    """
    user_context = user_context or {}
    
    # Se a tool exige confirmação explícita
    if getattr(tool, "requires_confirmation", False):
        confirmed = user_context.get("confirmed", False)
        # Se for tool de escrita/execução e o usuário não confirmou explicitamente, bloqueia execução direta
        if not confirmed:
            return False
            
    return True
