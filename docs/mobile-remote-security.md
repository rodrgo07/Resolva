# RESOLVA — Segurança do Controle Remoto Mobile

## 1. Zero Shell / Zero PowerShell / Zero SQL Arbitrário

A camada de controle remoto do RESOLVA possui restrições absolutas de segurança:
1. Não existe endpoint para execução de comandos do sistema operacional (nem CMD, nem PowerShell, nem Bash).
2. Não existe execução de SQL arbitrário pelo celular.
3. Não há exposição da porta ou banco SQLite bruto para a rede externa.
4. Toda e qualquer ação remota passa pelo catálogo rígido de comandos e pela **Permission Layer** (`READ -> SUGGEST -> PREPARE -> CONFIRM -> WRITE -> EXECUTE`).

---

## 2. Kill Switch & Proteção contra Replay

- Se o **Kill Switch** estiver ativado no Desktop, comandos como `EXECUTE_APPROVED_AUTOMATION` são imediatamente rejeitados com erro 403.
- Requisições duplicadas são ignoradas via `request_id` idempotente.
- Tentativas de prompt injection via textos de tarefas ou eventos são tratadas exclusivamente como `DATA`.
