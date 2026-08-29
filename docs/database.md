# 🗄️ RESOLVA — Documentação do Banco de Dados (Fase 2)

---

## 1. Estratégia de Migração (Alembic)

O banco de dados SQLite é gerenciado via **Alembic** utilizando migrations versionadas em `apps/backend/alembic/versions/`.

- **Versão inicial:** `63ed54c28728_initial_migration.py`
- **Comando para aplicar:**
  ```powershell
  $env:PYTHONPATH="apps/backend"
  .\.venv\Scripts\python.exe -m alembic -c apps/backend/alembic.ini upgrade head
  ```

---

## 2. Tabelas e Relacionamentos Criados

| Tabela | Descrição | Relacionamentos Principais |
| :--- | :--- | :--- |
| `categories` | Categorias unificadas (finanças, tarefas, estudos) | 1:N com `expenses`, 1:N com `budgets` |
| `expenses` | Registro financeiro (Receitas & Despesas) | N:1 com `categories` |
| `budgets` | Metas e limites de orçamento por categoria | N:1 com `categories` |
| `tasks` | Tarefas e afazeres com prazos, prioridades e tags | 1:N com `subtasks`, 1:N auto-referencial (parent_task) |
| `subtasks` | Checklist interno de cada tarefa | N:1 com `tasks` |
| `study_subjects`| Matérias e disciplinas de estudo com metas | 1:N com `study_sessions` |
| `study_sessions`| Registros de sessões Pomodoro ou Livre | N:1 com `study_subjects` |
| `calendar_events`| Compromissos e eventos com horários | Isolado com suporte a sincronização externa |
| `email_accounts`| Configuração de contas Gmail/Outlook/Mock | 1:N com `emails` |
| `emails` | Emails recebidos e triados por IA | N:1 com `email_accounts` |
| `automations` | Rotinas de automação cadastradas | 1:N com `automation_triggers`, `automation_actions`, `executions` |
| `automation_triggers` | Disparadores (manual, horário, evento) | N:1 com `automations` |
| `automation_actions` | Ações sequenciais seguras do sistema | N:1 com `automations` |
| `automation_executions` | Histórico e logs de execução | N:1 com `automations` |
| `notifications` | Central de notificações do app e sistema | Isolado por status/prioridade |
| `ai_conversations`| Histórico de conversas com o assistente | 1:N com `ai_messages` |
| `ai_messages` | Mensagens, chamadas de tools e retornos | N:1 com `ai_conversations` |
| `activity_logs` | Linha do tempo global de eventos e ações | Polimórfico por tipo e ação |
| `app_settings` | Chave-valor de configurações do usuário | Chave única indexada |

---

## 3. Seed de Dados de Demonstração

O script `apps/backend/seed/seed_data.py` popula o banco de dados com:
- 5 categorias financeiras e 2 orçamentos configurados
- 5 lançamentos (Receitas de R$ 3.500,00 e Despesas variadas)
- 4 tarefas com diferentes prioridades e 3 subtarefas
- 3 matérias de estudo (*Rust*, *FastAPI*, *IA*) com sessões registradas
- 2 eventos de calendário
- 1 automação modelo (*Modo Programação*)
- 3 notificações ativas e lidas
- Logs de atividade recentes e configurações de preferências

Para executar o seed manualmente:
```powershell
$env:PYTHONPATH="apps/backend"
.\.venv\Scripts\python.exe apps/backend/seed/seed_data.py
```
