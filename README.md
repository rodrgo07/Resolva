# RESOLVA ✨

> Seu centro de comando pessoal para organizar tarefas, estudos, finanças, agenda, e-mails, IA e automações em um único lugar.

O **RESOLVA** é um app desktop pensado para centralizar o que importa no dia a dia com uma experiência simples, prática e extensível.

## O que você encontra aqui 🚀

- 🖥️ Interface desktop com **React + Tauri**
- ⚙️ Backend assíncrono com **FastAPI**
- 🗄️ Persistência local com **SQLite**
- 🤖 Camada de IA com provedores `Mock`, `OpenAI` e `Local`
- 🔁 Automações com scheduler, templates e segurança reforçada

## Destaques 🌟

- 📊 Dashboard com visão consolidada do dia
- ✅ Gestão de tarefas, estudos, finanças, e-mails, calendário e atividade
- 🧠 Assistente de IA com ferramentas controladas por permissões
- ⏰ Automações manuais e agendadas
- 🛑 Kill switch global para pausar rotinas com segurança
- 🎯 Painel desktop com atalhos e navegação lateral

## Stack técnica 🛠️

- Desktop shell: Tauri v2 com Rust
- Frontend: React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, React Router, Lucide React, Recharts
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- Banco de dados: SQLite com `aiosqlite`
- Integrações: e-mail, notificações, calendário, tarefas, estudos e finanças

## Como começar 📦

### Pré-requisitos

- Node.js 18 ou superior
- Python 3.11 ou superior
- Rust e Cargo, para build do Tauri

### 1) Instalação inicial

Rode o setup para criar o ambiente virtual, instalar dependências e gerar o `.env`:

```powershell
.\scripts\setup.ps1
```

### 2) Rodar em desenvolvimento

Suba backend e frontend juntos:

```powershell
.\scripts\dev.ps1
```

Durante a execução:

- Frontend: http://localhost:1420
- Backend API: http://127.0.0.1:8700
- Swagger/OpenAPI: http://127.0.0.1:8700/docs

## Variáveis de ambiente 🔐

O arquivo `.env.example` mostra as principais variáveis do projeto. As mais importantes são:

- `BACKEND_HOST` e `BACKEND_PORT`
- `DATABASE_URL`
- `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`
- credenciais opcionais para Gmail e Outlook

## Testes 🧪

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

## Automações 🔁

O módulo de automações suporta:

- templates prontos para rotina da manhã, foco e revisão semanal
- execução manual e agendada
- ações tipadas e restritas por whitelist
- confirmação obrigatória para fluxos de maior risco
- kill switch global para suspensão imediata

Veja a documentação técnica em [`docs/automations.md`](docs/automations.md).

## Estrutura do repositório 🗂️

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

## Documentação útil 📚

- [`docs/automations.md`](docs/automations.md)
- [`apps/desktop/README.md`](apps/desktop/README.md)
