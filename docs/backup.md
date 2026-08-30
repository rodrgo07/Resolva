# Backup, Sincronização & Recuperação de Dados — RESOLVA

Este documento detalha a arquitetura, segurança e garantias de recuperação de dados do RESOLVA introduzidas na **Fase 25**.

---

## 1. Princípios Fundamentais

1. **Local-First:** O SQLite local permanece a única e definitiva fonte de verdade (`Source of Truth`).
2. **Offline-First:** Todas as entidades (tarefas, notas, finanças, estudos e e-mails já baixados) podem ser criadas e editadas sem conexão.
3. **Criptografia Integrada:** Backups gravados em disco são protegidos por **Windows DPAPI** (`CryptProtectData`), garantindo que apenas o usuário autorizado no dispositivo consiga descriptografar.
4. **Integridade SHA-256:** Cada backup possui um hash SHA-256 validado antes de qualquer restauração.
5. **Restauração com Rollback Atômico:** Antes de restaurar qualquer backup, o sistema gera automaticamente um snapshot `PRE_RESTORE`. Se a restauração falhar, o estado anterior é restabelecido sem perda de dados.
6. **Zero Exposição de Segredos:** Tokens OAuth, chaves de API e senhas são isolados e nunca incluídos nos backups ou payloads de sincronização.

---

## 2. Estrutura de Diretórios no Windows

- **Banco de dados ativo:** `%APPDATA%\Resolva\resolva.db` (ou diretório configurado em desenvolvimento)
- **Backups criptografados:** `%APPDATA%\Resolva\backups\resolva-backup-YYYY-MM-DD-HHMMSS.db.enc`
- **Identificador de Instalação (Device ID):** `%APPDATA%\Resolva\device.json`

---

## 3. Endpoints REST

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/backups` | `GET` | Lista todos os backups locais com metadados e integridade. |
| `/api/backups` | `POST` | Cria um novo backup criptografado sob demanda. |
| `/api/backups/{id}/restore` | `POST` | Restaura o banco de dados com snapshot pré-restore e confirmação explícita. |
| `/api/backups/{id}` | `DELETE` | Exclui fisicamente o arquivo de backup do disco. |
| `/api/sync/status` | `GET` | Retorna o status de conectividade, contagem da fila offline e conflitos. |
| `/api/sync/start` | `POST` | Dispara o processamento da fila de sincronização pendente. |
| `/api/sync/conflicts` | `GET` | Lista conflitos de sincronização registrados (Last-Write-Wins). |
