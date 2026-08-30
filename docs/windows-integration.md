# RESOLVA — Integração Nativa com Windows (Fase 26)

## 1. Visão Geral

A Fase 26 consolida o **RESOLVA** como um assistente pessoal residente de alta performance no ecossistema Windows, operando em segundo plano (System Tray), disponível instantaneamente via Global Hotkeys (ex: `Ctrl+Space`) e iniciando de forma segura e nativa com o sistema operacional, mantendo todas as camadas de segurança, permissões, sanitização e funcionamento offline-first.

---

## 2. Arquitetura de Integração com Windows

```
                                  SISTEMA OPERACIONAL WINDOWS
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
                GLOBAL HOTKEYS                                   SYSTEM TRAY
         (Ctrl+Space, Ctrl+Shift+T,                      (Ícone residente, menu de ações,
          Ctrl+Shift+A, Ctrl+Shift+P)                     status de sync, Kill Switch)
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                                  RESOLVA Tauri v2 Host
                               (Gerenciamento de Janelas,
                                Single Instance, Autostart)
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
               Quick Actions UI                                  Main Window
          (Command Palette Global,                        (Dashboard Glassmorphism,
           Quick Task, Pomodoro,                           Módulos completos)
           Expense, Event)                                             │
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                                    FastAPI Backend Sidecar
                                 (http://127.0.0.1:8700)
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       ▼                       ▼                       ▼
                  Agent Brain           AutomationEngine          SyncManager
               (AI Tools Catalog)       (ActionEngine)         (Offline-First Queue)
                       │                       │                       │
                       └───────────────────────┼───────────────────────┘
                                               ▼
                                    Permission & Safety Layer
                                  (Whitelist estrita, No Shell)
                                               │
                                               ▼
                                     SQLite (WAL Mode)
```

---

## 3. Global Hotkeys

Os atalhos globais são gerenciados pelo plugin oficial `tauri-plugin-global-shortcut` no host Rust e despachados para a interface via barramento de eventos:

- **`Ctrl+Space`**: Abre / foca instantaneamente o **Command Palette Global** do RESOLVA.
- **`Ctrl+Shift+T`**: Abre modal de **Criação Rápida de Tarefas**.
- **`Ctrl+Shift+A`**: Foca o **Resolva Agent** para conversação ou planejamento.
- **`Ctrl+Shift+P`**: Abre o **Timer Pomodoro Rápido**.

### Configuração Persistente
As teclas de atalho podem ser reconfiguradas ou desativadas nas configurações em `app_settings`:
- `hotkeys.command_palette`
- `hotkeys.quick_task`
- `hotkeys.agent`
- `hotkeys.pomodoro`

---

## 4. System Tray & Ciclo de Vida

O ícone residente no System Tray fornece acesso rápido às principais funções do aplicativo:
- **Abrir RESOLVA**: Restaura a janela principal.
- **Command Palette**: Dispara a busca rápida e paleta de comandos.
- **Nova Tarefa**: Abre modal de criação rápida.
- **Organizar meu dia**: Dispara o planejador diário do Agent.
- **Sincronização**: Mostra status e aciona sincronização imediata.
- **Criar Backup**: Gera snapshot criptografado sob demanda.
- **Pausar/Retomar Automações**: Aciona o **Kill Switch** global de segurança.
- **Configurações**: Abre a aba de configurações.
- **Sair**: Encerra de forma limpa todos os processos e conexões.

### Comportamento ao Fechar (`windows.close_behavior`)
- `minimize_to_tray` *(padrão)*: O clique no botão "X" esconde a janela principal, mantendo o backend, automações agendadas e hotkeys ativos em background.
- `exit_application`: O clique no "X" encerra completamente o processo Tauri e o backend.

---

## 5. Inicialização com o Windows (Startup)

Utiliza o mecanismo nativo de autostart via `tauri-plugin-autostart`:
- Sem uso de scripts `.bat` ou comandos arbitrários do PowerShell.
- Configuração reversível diretamente pela UI em *Configurações > Windows & Atalhos*.
- Suporte a inicialização minimizada ou direto no System Tray (`--autostart`).

---

## 6. Single Instance & Prevenção de Conflitos

- Implementado via `tauri-plugin-single-instance`.
- Impede a execução de múltiplas instâncias do aplicativo.
- Ao tentar abrir o RESOLVA novamente, a instância já em execução é restaurada e trazida ao primeiro plano.

---

## 7. Segurança & Princípio "Zero Arbitrary Shell"

1. **Zero Shell / PowerShell Livre**: Nenhuma ação ou comando permite que LLMs ou automações executem strings de shell no Windows.
2. **Whitelist Estrita de Aplicativos**: Apenas executáveis homologados (`ALLOWED_WINDOWS_APPS`) podem ser disparados.
3. **Validação de Riscos**: Ações de escrita e de execução exigem confirmação explícita ou permissão tipada.
4. **Isolamento de Credenciais**: Tokens OAuth protegidos pelo Windows DPAPI fora da base de dados principal.
