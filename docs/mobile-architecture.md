# RESOLVA Mobile — Arquitetura de Fundação Multidispositivo (Fase 28)

## 1. Princípios Arquiteturais

A evolução do ecossistema RESOLVA para ambientes multidispositivo adota estritamente os pilares:
- **LOCAL-FIRST**: O SQLite local do Desktop continua sendo a fonte primária da verdade (*Source of Truth*), enquanto o cliente Mobile mantém armazenamento e cache seguro local para operar em modo 100% desconectado.
- **OFFLINE-FIRST**: O aplicativo mobile permite visualizar e criar tarefas, finanças, compromissos e lembretes mesmo sem conectividade com o Desktop ou nuvem. As operações entram em uma fila local (*Offline Sync Queue*) e são processadas automaticamente assim que o link é restabelecido.
- **SECURITY-FIRST**: Não há dependência de canais de terceiros como bots de Discord. A comunicação direta entre Desktop e Mobile é autenticada com tokens criptográficos temporários, nonces e handshake de uso único.
- **ZERO SHELL**: Nenhuma operação ou comando permite execução de PowerShell, CMD ou SQL arbitrário originado remotamente.

---

## 2. Diagrama de Topologia de Rede & Sync

```
                        USUÁRIO
                           │
                           ▼
                    RESOLVA MOBILE
                     (Android/iOS)
                           │
                 [ Comunicação Segura ]
              (Sessão / Tokens / Assinatura)
                           │
                           ▼
                  RESOLVA SYNC LAYER
              (Device Identity, Auth, Sync)
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
     RESOLVA DESKTOP              FUTURO CLOUD RELAY
    (Windows / Tauri v2)           (Sync Broker E2E)
            │
            ▼
     FastAPI Backend
     (Agent / Tools)
            │
            ▼
      SQLite Local
    (Source of Truth)
```

---

## 3. Identidade dos Dispositivos & Handshake de Pareamento

- **Device ID Anônimo**: Cada instalação recebe um ID aleatório persistente (ex: `RESOLVA-MOBILE-A8F12B9D`).
- **Pareamento Seguro**:
  1. Desktop gera um código numérico de 6 dígitos (ex: `847 291`) e payload com nonce aleatório e expiração curta (5 minutos).
  2. O Mobile consome a requisição de pareamento via handshake.
  3. O código é invalidado imediatamente (*Single-use* / proteção contra replay).
  4. O Desktop armazena a sessão e gera `session_token` e `refresh_token` dedicados.
  5. O usuário pode renomear e revogar acessos de qualquer aparelho pelo painel Desktop em **Configurações > Dispositivos**.

---

## 4. Sync Engine, Idempotência & Resolução de Conflitos

- **Change Log Baseado em Operações**: O modelo de sincronização utiliza operações granulares (`CREATE_TASK`, `COMPLETE_TASK`, `CREATE_EXPENSE`, etc.) identificadas por `operation_id` universalmente único.
- **Garantia de Idempotência**: O reenvio de um mesmo `operation_id` não duplica registros na base de dados.
- **Resolução de Conflitos**: Utiliza metadados de versão e política determinística *Last-Write-Wins* (LWW), preservando integridade referencial e auditoria em `activity_logs`.
