import re
from typing import Dict, Any, Tuple, Optional

# Palavras-chave para triagem heurística / IA
CRITICAL_KEYWORDS = ["urgente", "emergência", "imediato", "bloqueio", "vencimento hoje", "fraude", "segurança da conta", "critical", "urgent", "asap"]
IMPORTANT_KEYWORDS = ["fatura", "pagamento", "boleto", "contrato", "proposta", "reunião", "alinhamento", "projeto", "resolva", "documento", "prazo", "vencimento"]
NEWSLETTER_KEYWORDS = ["newsletter", "unsubscribe", "descadastre-se", "no-reply", "noreply", "promoção", "oferta", "desconto", "marketing", "digest"]
REPLY_INDICATORS = ["aguardo retorno", "responda", "favor confirmar", "preciso que você", "me avise", "o que acha", "você pode", "let me know", "please reply"]

def classify_email(
    subject: str,
    from_address: str,
    from_name: Optional[str] = None,
    body_text: Optional[str] = None
) -> Tuple[str, Optional[str], bool]:
    """
    Classifica um email em categorias:
    CRITICAL, IMPORTANT, NORMAL, LOW, NEWSLETTER
    Retorna (classification, reasoning, needs_reply)
    """
    text_corpus = f"{subject} {from_name or ''} {body_text or ''}".lower()
    
    # 1. Checagem de Necessidade de Resposta
    needs_reply = False
    for rep in REPLY_INDICATORS:
        if rep in text_corpus:
            needs_reply = True
            break

    # 2. Checagem de Newsletter / Marketing
    for news in NEWSLETTER_KEYWORDS:
        if news in text_corpus or news in from_address.lower():
            return "NEWSLETTER", "Detectado padrão de informativo/marketing automático.", False

    # 3. Checagem de Crítico / Urgente
    for crit in CRITICAL_KEYWORDS:
        if re.search(rf"\b{re.escape(crit)}\b", text_corpus):
            return "CRITICAL", f"Termo prioritário '{crit}' identificado no conteúdo.", True

    # 4. Checagem de Importante
    for imp in IMPORTANT_KEYWORDS:
        if re.search(rf"\b{re.escape(imp)}\b", text_corpus):
            return "IMPORTANT", f"Assunto ou conteúdo de relevância profissional/financeira ('{imp}').", needs_reply

    # 5. Default
    if needs_reply:
        return "IMPORTANT", "A mensagem solicita confirmação ou resposta direta.", True

    return "NORMAL", "Mensagem de fluxo regular.", False
