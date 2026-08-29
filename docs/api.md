# 🔌 RESOLVA — Documentação da API REST (Fase 3)

---

## 1. Visão Geral da API

A API REST do **Resolva** é construída com **FastAPI** assíncrono e documentada automaticamente via Swagger/OpenAPI em `http://127.0.0.1:8700/docs`.

### Padrões de Resposta & Erros
- Tratamento de exceções com status codes padronizados (404 para recursos não encontrados, 422 para erros de validação, 403 para permissões e 400 para segurança de automação).
- Mensagens de erro amigáveis para o usuário em português.

---

## 2. Tabela Completa de Endpoints

### 🩺 Saúde do Sistema
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Status de execução, uptime e versão do backend. |

### ✅ Tarefas (`/api/tasks`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/tasks/` | Lista tarefas com paginação (`skip`, `limit`). |
| `POST` | `/api/tasks/` | Cria nova tarefa com subtarefas e tags opcionais. |
| `GET` | `/api/tasks/summary` | Resumo de tarefas (total, pendentes, concluídas, atrasadas). |
| `GET` | `/api/tasks/{id}` | Detalhes de uma tarefa específica e suas subtarefas. |
| `PUT` | `/api/tasks/{id}` | Atualiza título, prioridade, status e prazos. |
| `DELETE` | `/api/tasks/{id}` | Exclui tarefa e suas subtarefas. |
| `POST` | `/api/tasks/{id}/complete` | Marca tarefa como concluída e define `completed_at`. |
| `POST` | `/api/tasks/{id}/duplicate` | Duplica uma tarefa existente. |

### 💰 Finanças (`/api/finances`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/finances/transactions` | Lista lançamentos de receitas e despesas. |
| `POST` | `/api/finances/transactions` | Registra novo lançamento financeiro. |
| `GET` | `/api/finances/summary` | Total de receitas, despesas e saldo do período. |
| `GET` | `/api/finances/categories/breakdown` | Gastos agrupados por categoria com percentuais. |
| `GET` | `/api/finances/budgets` | Lista orçamentos e limites cadastrados. |
| `DELETE` | `/api/finances/transactions/{id}` | Exclui um lançamento financeiro. |

### 📚 Estudos (`/api/studies`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/studies/subjects` | Lista matérias e metas de estudo. |
| `POST` | `/api/studies/subjects` | Cadastra nova matéria. |
| `GET` | `/api/studies/summary` | Horas estudadas hoje, na semana e no mês. |
| `GET` | `/api/studies/subjects/{id}/sessions`| Histórico de sessões de uma matéria. |

### 📅 Agenda (`/api/calendar`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/calendar/` | Lista eventos e compromissos. |
| `POST` | `/api/calendar/` | Cria novo evento no calendário. |
| `GET` | `/api/calendar/{id}` | Detalhes do evento. |
| `PUT` | `/api/calendar/{id}` | Atualiza data, horário ou descrição do evento. |
| `DELETE` | `/api/calendar/{id}` | Exclui evento. |

### ✉️ Emails (`/api/emails`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/emails/` | Lista emails sincronizados com classificação de IA. |
| `GET` | `/api/emails/summary` | Contagem de não lidos, importantes e que precisam de resposta. |
| `POST` | `/api/emails/sync` | Dispara sincronização com provedor (Mock/Gmail/Outlook). |

### ⚡ Automações (`/api/automations`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/automations/` | Lista automações configuradas. |
| `POST` | `/api/automations/` | Cria nova rotina de automação. |
| `POST` | `/api/automations/{id}/run` | Executa rotina com validação de segurança e logs. |
| `GET` | `/api/automations/{id}/executions` | Histórico de auditoria de execuções. |

### 🤖 IA & Chat (`/api/ai`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/ai/chat` | Envia mensagem para o agente, executa tools permitidas e persiste histórico. |
| `GET` | `/api/ai/conversations` | Lista conversas anteriores. |
| `GET` | `/api/ai/conversations/{id}` | Recupera mensagens de uma conversa específica. |

### 🔔 Notificações, Atividades & Busca
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/notifications/` | Lista notificações do sistema. |
| `POST` | `/api/notifications/read-all` | Marca todas como lidas. |
| `GET` | `/api/activity/` | Linha do tempo de atividades recentes. |
| `GET` | `/api/search/?q={query}` | Busca global unificada em todas as entidades. |
| `GET` | `/api/settings/` | Consulta preferências do aplicativo. |
