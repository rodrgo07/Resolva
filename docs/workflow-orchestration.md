# Workflow Chains & Dependencies (Fase 34)

## 1. Encadeamento Seguro (Chains)
Permite a orquestração de múltiplos workflows em sequência lógica. Cada etapa avalia o resultado da anterior e respeita as políticas de falha:
- FAIL_FAST: Interrompe a cadeia imediatamente.
- CONTINUE: Prossegue com as etapas independentes.
- RETRY: Tenta recuperação controlada.
- ASK_USER: Solicita decisão ao usuário via confirmação explícita.
