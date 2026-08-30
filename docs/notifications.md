# RESOLVA — Central de Notificações Inteligentes & Agente Proativo (Fase 27)

## 1. Visão Geral

A **Fase 27** evolui o RESOLVA de uma aplicação responsiva para um **assistente pessoal altamente proativo e preditivo**. O sistema monitora de forma autônoma e em segundo plano o estado das tarefas, compromissos na agenda, e-mails recebidos, sessões de estudo, finanças e rotinas, gerando alertas no momento certo sem sobrecarregar o usuário (anti-spam, deduplicação e Quiet Hours).

---

## 2. Arquitetura do Sistema de Notificações

```
                                  RESOLVA AGENT / ANALYZERS
                     (TaskAnalyzer, CalendarAnalyzer, EmailAnalyzer,
                      StudyAnalyzer, FinanceAnalyzer, ProactiveAgent)
                                               │
                                               ▼
                                      NotificationEngine
                                 (Deduplicação, Priorização)
                                               │
                                               ▼
                                      NotificationPolicy
                               (Quiet Hours, Anti-Spam, Filtros)
                                               │
                                               ▼
                                    NotificationRepository
                                 (SQLite WAL, Retenção 30d)
                                               │
                                               ▼
                                    NotificationDispatcher
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       ▼                       ▼                       ▼
                 Windows Toast           In-App Center            System Tray
             (Tauri Notification)     (/notifications page)      (Badge & Menus)
                                               │
                                               ▼
                                         Quick Actions
                                   (Safe, Permission-Checked)
```

---

## 3. Tipos e Prioridades de Notificação

### Tipos Homologados:
- `TASK_OVERDUE`: Tarefa vencida ou grupo de tarefas em atraso.
- `CALENDAR_UPCOMING`: Compromisso iminente (15m, 30m, 1h).
- `EMAIL_IMPORTANT` / `EMAIL_URGENT`: E-mails priorizados pela inteligência artificial.
- `STUDY_REMINDER`: Lembrete de bloco Pomodoro ou estudo diário.
- `FINANCE_ALERT`: Alertas e balanços semanais de despesas/receitas.
- `AGENT_RECOMMENDATION`: Sugestões contextuais e planejamento matinal do Agent.
- `SYNC_STATUS` & `AUTOMATION_RESULT`: Status de rotinas e conectividade offline-first.

### Níveis de Prioridade:
1. `CRITICAL`: Evento iminente em <15min, alertas críticos.
2. `URGENT`: Tarefas vencidas com prioridade alta, compromissos em 30min.
3. `IMPORTANT`: E-mails importantes, tarefas próximas do prazo.
4. `NORMAL`: Lembretes padrão e resumos do dia.
5. `LOW`: Recomendações opcionais e dicas contextuais.

---

## 4. Políticas de Anti-Spam e Quiet Hours

- **Deduplicação Inteligente**: Baseada em chave lógica `source + source_id + type` em janela temporal de 60 minutos. Evita criação de notificações duplicadas a cada tick do scheduler.
- **Quiet Hours**: Horário noturno configurável (ex: `22:00` às `07:00`). Suprime alertas `LOW` e `NORMAL`, permitindo apenas `CRITICAL` se configurado pelo usuário.
- **Retenção e Limpeza Automática**: Notificações lidas ou dispensadas há mais de 30 dias são expurgadas automaticamente sem acumular lixo no SQLite.

---

## 5. Integração com o Resolva Agent & AI Tools

O catálogo padrão de ferramentas do Agent foi enriquecido com:
- `get_notifications`: Consulta paginada de notificações com filtros.
- `get_notification_summary`: Resumo de não lidas, urgentes e distribuição.
- `mark_notification_read`: Marca notificação como lida.
- `dismiss_notification`: Descarta/dispensa notificação ativa.
- `create_notification`: Cria lembretes proativos e avisos contextuais.
- `get_notification_preferences`: Consulta configurações ativas de notificação.

---

## 6. Segurança e Permission Layer

- **Zero Shell / Zero Scripts**: Nenhuma notificação executa código arbitrário.
- **Validação Estrita de Ações Seguras**: Ações como `COMPLETE_TASK` exigem validação e confirmação explícita.
- **Tratamento de Dados de E-mail**: Textos e remetentes são tratados puramente como dados (`DATA`), neutralizando tentativas de prompt injection.
