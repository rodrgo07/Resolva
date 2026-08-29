# 🤖 RESOLVA — Documentação de IA & AI Tools (Fase 11)

---

## 1. Arquitetura do Orquestrador de IA

O **Resolva AI** utiliza um fluxo de chamadas a ferramentas (*Function Calling* / *Tool Use*) com abstração de múltiplos provedores e barramento de permissões:

```
[ Usuário ] 
    │ (mensagem)
    ▼
[ AIOrchestrator ] ─── Envia mensagens + Schemas de Tools ───► [ LLM / Provider ]
    │                                                                   │
    │ ◄── Recebe resposta com chamadas de ferramenta (ToolCalls) ───────┘
    │
    ├─► [ Permission Layer ] (Verifica se READ / WRITE / EXECUTE é permitido)
    ├─► [ Tool Execution ] (Executa a ferramenta no Banco de Dados / Sistema)
    │
    ▼
[ AIOrchestrator ] ─── Envia histórico + Resultados das Tools ──► [ LLM / Provider ]
    │
    ▼ (Resposta Final em Linguagem Natural + Lista de Tools Executadas)
[ Interface Desktop ]
```

---

## 2. Catálogo de AI Tools Implementadas

| Ferramenta | Permissão | Descrição | Parâmetros |
| :--- | :---: | :--- | :--- |
| `list_tasks` | `READ` | Consulta tarefas no banco filtradas por status. | `status` (*pendente*, *em_andamento*, *concluida*, *all*) |
| `create_task` | `WRITE` | Cria uma nova tarefa com prioridade e categoria. | `title` (*obrigatório*), `priority`, `category` |
| `get_finance_summary`| `READ` | Retorna total de receitas, despesas e saldo do período. | `days` (dias de histórico, padrão: 30) |
| `create_expense` | `WRITE` | Registra uma nova despesa no módulo financeiro. | `amount`, `description`, `category_id` |
| `get_study_summary`| `READ` | Retorna horas estudadas hoje, na semana e no mês. | Nenhum |

---

## 3. Configuração de Provedores

No arquivo `.env`:
- **Modo Demonstração / Offline:** `AI_PROVIDER=mock`
- **Modo OpenAI:**
  ```ini
  AI_PROVIDER=openai
  AI_API_KEY=sk-...
  AI_MODEL=gpt-4o-mini
  ```
