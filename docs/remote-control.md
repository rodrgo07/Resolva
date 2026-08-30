# RESOLVA — Controle Remoto Seguro & Permission Layer (Fase 29)

## 1. Visão Geral

A **Fase 29** transforma o RESOLVA Mobile em um painel de controle remoto autorizado do RESOLVA Desktop. O controle remoto foi desenhado com segurança absoluta:
- **Zero Shell / Zero PowerShell / Zero SQL Arbitrário**: Não há canais para execução de comandos livres no sistema operacional.
- **Catálogo Homologado**: Apenas operações cadastradas (`GET_DESKTOP_STATUS`, `CREATE_TASK`, `START_POMODORO`, `SYNC_NOW`, `CREATE_BACKUP`, `EXECUTE_APPROVED_AUTOMATION`) podem ser executadas.
- **Permission Layer & Confirmação Remota**: Ações de risco elevado (como disparar rotinas ou apagar registros) exigem confirmação explícita no dispositivo antes da execução.

---

## 2. Fluxo de Confirmação Remota

```
┌─────────────────┐                                  ┌─────────────────┐
│ RESOLVA Mobile  │                                  │ RESOLVA Backend │
└────────┬────────┘                                  └────────┬────────┘
         │                                                    │
         │ 1. POST /api/remote/commands                       │
         │    (command_type: EXECUTE_APPROVED_AUTOMATION)     │
         │───────────────────────────────────────────────────>│
         │                                                    │ 2. Detecta risco MEDIUM
         │                                                    │    Gera RemotePendingAction
         │ 3. Status: PENDING_CONFIRMATION (action_id)        │
         │<───────────────────────────────────────────────────│
         │                                                    │
         │ 4. Exibe Modal/Alert no celular                    │
         │    "Deseja confirmar a execução?"                 │
         │                                                    │
         │ 5. POST /api/remote/actions/confirm (confirmed=true)│
         │───────────────────────────────────────────────────>│
         │                                                    │ 6. Valida expiração & ID
         │                                                    │    Executa rotina
         │                                                    │    Audita em activity_logs
         │ 7. Retorna Status: EXECUTED + Result               │
         │<───────────────────────────────────────────────────│
```

---

## 3. Idempotência e Proteção Contra Replay

- Todas as requisições utilizam `request_id` único gerado pelo cliente.
- Requisições duplicadas não reexecutam tarefas ou gastos na base de dados, retornando o resultado original previamente armazenado na tabela `remote_commands`.
