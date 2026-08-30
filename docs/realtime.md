# RESOLVA — Comunicação em Tempo Real via WebSocket (Fase 29)

## 1. Arquitetura Realtime

```
┌──────────────────┐               EventBus                ┌──────────────────┐
│ RESOLVA Services ├──────────────────────────────────────>│ Realtime Manager │
└──────────────────┘                                       └────────┬─────────┘
                                                                    │ WebSocket
                                                                    ▼
                                                            ┌──────────────────┐
                                                            │  RESOLVA Mobile  │
                                                            │ (Zustand Store)  │
                                                            └──────────────────┘
```

---

## 2. Eventos Homologados

- `TASK_CREATED`, `TASK_COMPLETED`, `TASK_UPDATED`
- `EVENT_CREATED`, `EVENT_UPDATED`
- `EXPENSE_CREATED`
- `STUDY_SESSION_STARTED`, `STUDY_SESSION_COMPLETED`
- `SYNC_COMPLETED`, `BACKUP_CREATED`
- `REMOTE_COMMAND_EXECUTED`
- `DEVICE_CONNECTED`, `DEVICE_REVOKED`

---

## 3. Heartbeat e Reconexão com Backoff

- Pings periódicos a cada 15 segundos mantêm a conexão viva.
- Em caso de desconexão, o `RealtimeClient` no Mobile executa reconexão com *exponential backoff* (1s, 2s, 4s, 8s, 15s) sem travar a interface do usuário.
