# RESOLVA — Sincronização Mobile & Fila Offline

## 1. Modelo de Fila Offline Local-First

No cliente **RESOLVA Mobile**, todas as ações do usuário (criar tarefas, adicionar despesas, marcar notificações como lidas) são persistidas instantaneamente na fila local:
- O estado da interface reage em tempo real (latência zero).
- Quando o dispositivo está sem conexão, um indicador visual exibe `○ Offline` e a contagem de itens em fila (`⚡ N alterações pendentes`).
- Ao restabelecer a conectividade com o Desktop, o `MobileSyncEngine` envia as operações pendentes em lote através de `POST /api/sync/push`.

---

## 2. Idempotência e Change Log

- Cada operação recebe um `operation_id` universalmente único gerado no cliente.
- Ao receber o push, o servidor valida se o `operation_id` já foi gravado na tabela `sync_operations`.
- Se já existir, a operação é ignorada sem duplicação de dados, retornando sucesso na lista `processed_operation_ids`.
