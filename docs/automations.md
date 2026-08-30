# Sistema de Automações & Rotinas Inteligentes — RESOLVA

Este documento detalha o funcionamento, arquitetura e garantias de segurança do módulo de **Automações e Rotinas** do RESOLVA.

---

## 1. Arquitetura

```
                 ┌──────────────────────────┐
                 │       RESOLVA AGENT      │
                 │   (Automation Planner)   │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │   Automation Definition  │
                 │(Draft, Triggers & Actions│
                 └────────────┬─────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │TriggerEngine │  │ConditionEng. │  │ ActionEngine │
     │  (Schedule/  │  │(Horários,    │  │ (Whitelist   │
     │   Startup)   │  │ E-mails, DB) │  │  Sandbox)    │
     └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                 ┌──────────────────────────┐
                 │ AutomationPermissionServ.│
                 │   (Risco, Kill Switch &  │
                 │  Confirmação Obrigatória)│
                 └────────────┬─────────────┘
                              ▼
                 ┌──────────────────────────┐
                 │   AutomationExecution    │
                 │   (Auditoria & Logs)     │
                 └──────────────────────────┘
```

---

## 2. Whitelist de Ações e Aplicativos

O RESOLVA adota uma política restrita de segurança:
- **Sem Shell Arbitrário:** Comandos de terminal, PowerShell livre e queries SQL brutas são completamente bloqueados.
- **Whitelist de Aplicativos Windows:** Abertura restrita a executáveis homologados (`vscode`, `chrome`, `edge`, `firefox`, `spotify`, `discord`, `notepad`, `calc`).
- **Ações Tipadas:**
  - `CREATE_NOTIFICATION`
  - `SHOW_AGENT_MESSAGE`
  - `CREATE_TASK`
  - `COMPLETE_TASK`
  - `START_STUDY_SESSION`
  - `CREATE_CALENDAR_EVENT`
  - `SYNC_EMAIL`
  - `GENERATE_DAILY_SUMMARY` / `GENERATE_WEEKLY_SUMMARY`
  - `OPEN_APPLICATION`

---

## 3. Kill Switch & Rate Limit

- **Kill Switch Global:** Permite suspender e reativar imediatamente todas as rotinas em execução no sistema com um único clique no painel ou via API REST.
- **Rate Limit & Idempotência:** Cooldown mínimo de 2 segundos entre execuções manuais e locks em memória para impedir execuções simultâneas da mesma automação.

---

## 4. Templates de Rotinas Integrados

1. **Rotina da Manhã:** Abre o ambiente de desenvolvimento (VS Code), dispara mensagem do Agent e sincroniza e-mails prioritários.
2. **Foco & Sessão de Estudos:** Dispara notificação de foco e inicializa um bloco Pomodoro de 25 minutos.
3. **Revisão Semanal:** Gera resumo de tarefas, estudos e finanças no domingo às 20:00.
