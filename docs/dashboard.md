# Central Inteligente de Comando — Dashboard & Agent UX (RESOLVA)

Este documento descreve a arquitetura, endpoints e fluxos operacionais da **Central de Comando Inteligente** introduzida na Fase 24 do RESOLVA.

---

## 1. Visão Geral da Central de Comando

O Dashboard do RESOLVA opera como o centro operacional diário do usuário, respondendo constantemente à pergunta: **"O que eu deveria fazer agora?"**.

```
                   ┌──────────────────────────────────────┐
                   │    CENTRAL DE COMANDO (Dashboard)    │
                   └──────────────────┬───────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐
  │ Card 'AGORA' │             │Resumo do Dia │             │ Timeline do  │
  │(Foco Imediato│             │(Tarefas, Cal,│             │     Dia      │
  │  Prioritário)│             │ Emails, Meta)│             │(Cronológico) │
  └──────────────┘             └──────────────┘             └──────────────┘
                                      ▲
                                      │
                   ┌──────────────────┴───────────────────┐
                   │           DashboardService           │
                   │ (Agregação paralela e determinística)│
                   └──────────────────┬───────────────────┘
                                      │
         ┌──────────────┬─────────────┴┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼              ▼
      Tarefas        Agenda         Emails         Estudos        Finanças
```

---

## 2. Endpoints REST da Central de Comando

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/dashboard/overview` | `GET` | Agregação completa de contagens de tarefas, e-mails, horas estudadas e despesas. |
| `/api/dashboard/now` | `GET` | Determinação algorítmica da ação mais crítica do momento. |
| `/api/dashboard/timeline` | `GET` | Linha do tempo cronológica com eventos, prazos e rotinas de hoje. |
| `/api/dashboard/recommendations` | `GET` | Recomendações dinâmicas e contextuais de produtividade. |

---

## 3. Heurística de Prioridade do Card "AGORA"

1. **Urgência 1 (Crítico):** Tarefas com prazo vencido (`overdue > 0`).
2. **Urgência 2 (Alta):** E-mails classificados como críticos/urgentes pela IA aguardando resposta.
3. **Urgência 3 (Média):** Próximo compromisso agendado no calendário.
4. **Urgência 4 (Normal):** Sessão de estudo Pomodoro recomendada para manter a meta diária.
5. **Estado Livre (Baixa):** "Tudo em dia" com atalho para o planejador diário do Agent.
