# 🟣 RESOLVA — Centro de Comando Pessoal

> "O que eu preciso saber, fazer ou resolver agora?"

O **RESOLVA** é um assistente pessoal digital para desktop que centraliza produtividade, tarefas, rotina de estudos, finanças pessoais, agenda, automações de sistema e inteligência artificial orientada a ferramentas.

---

## 🏗️ Arquitetura e Stack

- **Desktop Shell:** Tauri v2 (Rust)
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, Lucide React, Recharts
- **Backend:** Python 3.11+, FastAPI (assíncrono), SQLAlchemy 2.0, Alembic, Pydantic v2
- **Banco de Dados:** SQLite (com driver assíncrono `aiosqlite`)
- **Engine de IA:** Camada de orquestração com abstração de provedores (`Mock`, `OpenAI`, `Local`) e barramento seguro de permissões para AI Tools.
- **Automação:** Executor de rotinas locais com lista de comandos permitidos e logs de auditoria.

---

## 🚀 Como Iniciar o Projeto

### Pré-requisitos
- Node.js ≥ 18
- Python ≥ 3.11
- Rust & Cargo (para build nativo do Tauri)

### 1. Configuração Inicial

Execute o script de setup para criar o ambiente virtual Python, instalar dependências e preparar o arquivo `.env`:

```powershell
.\scripts\setup.ps1
```

### 2. Executar em Modo de Desenvolvimento

Inicie o backend e o frontend simultaneamente:

```powershell
.\scripts\dev.ps1
```

- **Frontend:** [http://localhost:1420](http://localhost:1420)
- **Backend API:** [http://127.0.0.1:8700](http://127.0.0.1:8700)
- **Documentação OpenAPI/Swagger:** [http://127.0.0.1:8700/docs](http://127.0.0.1:8700/docs)

---

## 🧪 Testes

### Backend (pytest)
```powershell
$env:PYTHONPATH="apps/backend"
.\.venv\Scripts\python.exe -m pytest apps\backend\tests
```

### Frontend (Typecheck & Build)
```powershell
cd apps/desktop
npm run build
```

---

## 📂 Estrutura do Repositório

```
resolva/
├── apps/
│   ├── desktop/          # Frontend React + Tauri Shell
│   └── backend/          # Backend FastAPI + SQLAlchemy + AI + Automações
├── docs/                 # Documentações de arquitetura, banco e roadmap
├── scripts/              # Scripts de setup e inicialização (PowerShell)
├── .env.example          # Variáveis de ambiente de exemplo
└── README.md
```