# Conflict Resolution & Advanced Delta Sync (Fase 32)

## 1. Arquitetura de Delta Sync
Cada modificação em entidades sincronizáveis (tarefas, notas, planos, memórias) trafega no formato de delta com base_version e resulting_version.

## 2. Resolução de Conflitos Determinística (CRDT-like)
- **NON_CONFLICTING / FIELD_CONFLICT**: Modificações em campos disjuntos são combinadas automaticamente.
- **CONTENT_CONFLICT (Texto)**: Se uma versão contém a outra como expansão linear, o merge é automático.
- **USER_REQUIRED**: Se ambas as pontas editaram o mesmo campo de forma conflitante, o conflito é colocado em quarentena na tabela advanced_sync_conflicts para decisão explícita do usuário.
