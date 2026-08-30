# RESOLVA — Segurança, Isolamento de Segredos & Permission Layer no Mobile

## 1. Zero Shell / Zero PowerShell / Zero SQL Arbitrário

A camada de comunicação e sincronização multidispositivo foi desenhada com segurança estrita:
- Nenhuma API expõe execução de shell ou comandos arbitrários no sistema operacional.
- O Mobile acessa exclusivamente ações homologadas e validadas pela `Permission Layer` do RESOLVA Agent (`READ -> SUGGEST -> PREPARE -> CONFIRM -> WRITE -> EXECUTE`).
- Ações destrutivas (ex: exclusão de dados) exigem confirmação explícita do usuário.

---

## 2. Isolamento Total de Segredos e Tokens OAuth

- Os tokens de acesso e refresh do Google OAuth (Gmail) e Microsoft OAuth (Outlook) residem exclusivamente no **Cofre DPAPI / Vault Seguro** do RESOLVA Desktop.
- O payload de sincronização e os DTOs de bootstrap mobile **nunca** incluem credenciais de provedores externos, chaves de API de LLMs ou arquivos SQLite brutos.
- As requisições originadas do Mobile utilizam tokens de sessão (`session_token`) independentes que podem ser revogados a qualquer momento no Desktop.
