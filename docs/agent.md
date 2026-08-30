# RESOLVA AGENT — Documentação de Arquitetura & Produtividade Pessoal

O **RESOLVA AGENT** é o orquestrador central e assistente autônomo do RESOLVA, projetado para unificar a gestão de tarefas, agenda, e-mails (Gmail & Outlook), finanças, estudos e automações locais com segurança de dados e privacidade em primeiro lugar.

---

## 1. Arquitetura do Agent

```
                          ┌──────────────────────────┐
                          │       RESOLVA AGENT      │
                          │   (Orquestrador Central) │
                          └─────────────┬────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
    ┌──────────────┐             ┌──────────────┐             ┌──────────────┐
    │ContextEngine │             │PlanningEngine│             │    Memory    │
    │(Resumo Diário│             │(Time Blocks &│             │(Histórico &  │
    │  Estruturado)│             │ Priorização) │             │  Auditoria)  │
    └──────┬───────┘             └──────┬───────┘             └──────┬───────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │     Permission Layer     │
                          │(READ, SUGGEST, PREPARE,  │
                          │ CONFIRM, WRITE, EXECUTE) │
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │    AI Tools Catalog      │
                          │(Tarefas, E-mails, Agenda,│
                          │  Finanças, Estudos, Auto)│
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │  Módulos Locais SQLite   │
                          │(Nenhum SQL direto do LLM)│
                          └──────────────────────────┘
```

---

## 2. Princípios de Segurança e Prevenção a Injeções

1. **Sem Acesso Arbitrário:** O LLM não possui acesso ao shell, terminal, sistema de arquivos livre ou queries SQL diretas.
2. **Whitelist Estrita de Ferramentas:** Toda operação é executada exclusivamente através de classes derivadas de `BaseTool`.
3. **Isolamento de Dados Externos (Prompt Injection Defense):** Conteúdos de e-mails, títulos de tarefas e mensagens de terceiros são tratados estritamente como **DADOS** em envelopes estruturados e nunca como instruções de controle do sistema.
4. **Confirmação Obrigatória para Escrita/Execução:**
   - Ferramentas destrutivas (`delete_task`, `archive_email`) ou de alto impacto (`execute_automation`, `send_email`) exigem confirmação explícita do usuário antes de rodar.

---

## 3. Níveis de Permissão & Risk Levels

| Nível | Descrição | Exemplo de Tool | Requer Confirmação |
| :--- | :--- | :--- | :--- |
| **READ** | Consultas e resumos de contexto | `get_today_context`, `get_unread_emails` | Não |
| **SUGGEST** | Criação de planos diários e recomendações | `organize_my_day` | Não |
| **PREPARE** | Elaboração prévia de ações para aprovação | `prepare_email_reply` | Não |
| **WRITE** | Criação e alteração de entidades no banco | `complete_task`, `delete_task` | Sim |
| **EXECUTE** | Disparo de automações no Windows | `execute_automation` | Sim |

---

## 4. Context Engine & Planejador Diário

- **`ContextEngine`:** Monta visões resumidas e compactas sob demanda (`get_today_context`), contendo tarefas atrasadas, compromissos de hoje, e-mails não lidos de alta prioridade e estatísticas recentes.
- **`PlanningEngine`:** Transforma metas do usuário em uma rotina diária dividida em:
  - **Alta Prioridade:** Pendências com prazo vencido e e-mails críticos.
  - **Média Prioridade:** Afazeres regulares agendados para hoje.
  - **Blocos de Tempo:** Estruturação de foco matutino, reuniões e sessões de estudo.

---

## 5. Auditoria & Observabilidade

- Todas as ações executadas pelo Agent são registradas na tabela de auditoria (`ActivityLog`).
- O usuário pode visualizar e limpar o histórico de atividades a qualquer momento pelo drawer de auditoria no painel `/agent`.
- Informações sensíveis (tokens OAuth, senhas ou chaves de API) são filtradas e nunca persistidas nos logs.
