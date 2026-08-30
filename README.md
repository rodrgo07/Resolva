# RESOLVA

O **RESOLVA** é um centro de comando pessoal para desktop que reúne produtividade, tarefas, estudos, finanças, agenda, e-mails, IA orientada a ferramentas e automações locais em uma única interface.

## Visão geral

O projeto é dividido em dois aplicativos principais:

- `apps/desktop`: interface desktop em React + Tauri
- `apps/backend`: API assíncrona em FastAPI com persistência em SQLite

Além do fluxo principal de organização pessoal, o RESOLVA já inclui um módulo de automações com rotinas agendadas, templates prontos, kill switch global e validações de segurança.

## Stack

- Desktop shell: Tauri v2 com Rust
- Frontend: React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, React Router, Lucide React, Recharts
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- Banco de dados: SQLite com `aiosqlite`
- IA: camada de orquestração com provedores `Mock`, `OpenAI` e `Local`
- Integrações: e-mail, notificações, calendário, tarefas, estudos e finanças

## Funcionalidades

- Dashboard com visão consolidada do dia
- Gestão de tarefas, estudos, finanças, e-mails, calendário e atividade
- Assistente de IA com ferramentas controladas por permissões
- Automações com templates, scheduler persistente e auditoria
- Kill switch global para pausar rotinas em execução
- Painel desktop com atalhos e navegação lateral

## Começando

### Pré-requisitos

- Node.js 18 ou superior
- Python 3.11 ou superior
- Rust e Cargo, para o build do Tauri

### 1. Instalação inicial

Execute o script de setup para criar o ambiente virtual, instalar dependências e gerar o arquivo `.env` a partir do exemplo:

```powershell
.\scripts\setup.ps1
```

### 2. Desenvolvimento

Inicie backend e frontend ao mesmo tempo:

```powershell
.\scripts\dev.ps1
```

Durante a execução, os serviços ficam disponíveis em:

- Frontend: http://localhost:1420
- Backend API: http://127.0.0.1:8700
- Swagger/OpenAPI: http://127.0.0.1:8700/docs

## Variáveis de ambiente

O arquivo `.env.example` documenta as principais variáveis do projeto. As mais importantes são:

- `BACKEND_HOST` e `BACKEND_PORT`
- `DATABASE_URL`
- `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`
- credenciais opcionais para Gmail e Outlook

## Testes

### Backend

```powershell
$env:PYTHONPATH="apps/backend"
.\.venv\Scripts\python.exe -m pytest apps\backend\tests
```

### Frontend

```powershell
cd apps/desktop
npm run build
```

## Automações

O módulo de automações suporta:

- templates prontos para rotina da manhã, foco e revisão semanal
- execução manual e agendada
- ações tipadas e restritas por whitelist
- confirmação obrigatória para fluxos de maior risco
- kill switch global para suspensão imediata

Consulte `docs/automations.md` para a visão técnica do módulo.

## Estrutura do repositório

```text
resolva/
├── apps/
│   ├── desktop/          # Frontend React + Tauri
│   └── backend/          # API FastAPI, IA, automações e integrações
├── docs/                  # Documentação técnica
├── scripts/               # Scripts PowerShell de setup e dev
├── .env.example           # Exemplo de variáveis de ambiente
└── README.md
```

## Documentação útil

- `docs/automations.md`
- `apps/desktop/README.md`
