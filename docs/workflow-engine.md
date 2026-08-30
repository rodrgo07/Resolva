# Workflow Engine & Automation Intelligence (Fase 33)

## 1. Visão Geral
O Workflow Engine do RESOLVA transforma o sistema de automações em um motor declarativo, determinístico, seguro e auditável, perfeitamente integrado ao Resolva Agent e ao ecossistema multidispositivo.

## 2. Ciclo de Vida do Workflow
- **DRAFT**: Rascunho inicial gerado pelo usuário ou sugerido pelo Agent via linguagem natural.
- **ACTIVE**: Habilitado para disparos por horário, eventos do EventBus ou chamadas manuais.
- **PAUSED / DISABLED**: Suspenso temporariamente sem perda de configuração.
- **RUNNING**: Execução em progresso com etapas sequenciais ordenadas.
- **WAITING_CONFIRMATION**: Pausado aguardando autorização do usuário no Desktop ou Mobile.
- **COMPLETED / FAILED / CANCELLED / PARTIAL_FAILURE**: Estados finais auditados.
