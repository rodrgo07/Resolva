# Guia de Integração de E-mail (Gmail & OAuth 2.0) - RESOLVA

Este documento orienta sobre a integração real de e-mails no **RESOLVA**, abordando o fluxo de autenticação OAuth 2.0, segurança no armazenamento de credenciais, sincronização incremental e triagem inteligente por IA.

---

## 1. Visão Geral da Arquitetura

A integração de e-mails foi estruturada com base no padrão Provider (`EmailProvider`):

- **GmailProvider**: Integração real utilizando a API REST oficial do Gmail (`google-api-python-client` / endpoints HTTPS diretos com OAuth 2.0 PKCE / Desktop App loopback).
- **OutlookProvider**: Abstração preparada para integração futura com Microsoft Graph API.
- **MockEmailProvider**: Provedor local para desenvolvimento, modo offline e execução de testes automatizados no CI.

---

## 2. Configuração no Google Cloud Console

Para conectar uma conta real do Gmail, siga o passo a passo:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto (ex: `Resolva-Desktop`).
3. Vá em **APIs e Serviços > Biblioteca** e ative a **Gmail API**.
4. Acesse **APIs e Serviços > Tela de permissão OAuth**:
   - Escolha o tipo de usuário: **Externo** (External).
   - Preencha o nome do app (`Resolva`) e o e-mail de suporte.
   - Adicione os seguintes escopos (*Scopes*):
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
     - `https://www.googleapis.com/auth/gmail.modify`
   - Em **Usuários de teste**, adicione o seu e-mail do Gmail para autorizar durante o período de desenvolvimento.
5. Acesse **APIs e Serviços > Credenciais**:
   - Clique em **+ Criar Credenciais > ID do cliente OAuth**.
   - Tipo de aplicativo: **App para computador** (Desktop Application).
   - Copie o **Client ID** e o **Client Secret** gerados.
6. Configure no arquivo `.env` do Resolva:
   ```env
   GMAIL_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=seu_client_secret_aqui
   ```

---

## 3. Armazenamento Seguro de Tokens (Token Storage Vault)

O **RESOLVA** não armazena tokens de acesso ou de atualização (`access_token`, `refresh_token`) em texto puro no banco SQLite.

- **Mecanismo:** No Windows, o sistema utiliza DPAPI (`CryptProtectData` e `CryptUnprotectData`) com chave derivada da máquina do usuário.
- **Localização:** Os arquivos criptografados residem no diretório isolado `%APPDATA%\Resolva\credentials\`.
- **Banco SQLite:** Mantém apenas metadados públicos (endereço de e-mail, status de sincronização, horários e paginação).

---

## 4. Sincronização Incremental e Limites

- **Limite Inicial:** A sincronização inicial busca no máximo os **100 e-mails mais recentes** para preservar consumo de banda e desempenho.
- **Idempotência:** E-mails são salvos e identificados pelo `external_id` (ID oficial do provedor), impedindo duplicidades.
- **Offline-First:** Caso a conexão caia, todos os e-mails previamente baixados permanecem disponíveis localmente para leitura e pesquisa.

---

## 5. Triagem e Classificação por IA

Ao receber novas mensagens, o serviço executa a triagem categorizando em:
- `CRITICAL`: Notificações urgentes, bloqueios ou alertas de emergência.
- `IMPORTANT`: Faturas, pagamentos, contratos ou projetos.
- `NORMAL`: E-mails comuns de trabalho e mensagens diretas.
- `LOW`: E-mails informativos secundários.
- `NEWSLETTER`: Informativos e promoções automáticas.

A IA pode ser consultada através das novas AI Tools integradas (`list_important_emails`, `search_emails`, `get_unread_emails`, `get_email_summary`, `archive_email`).

---

## 6. Ações de Escrita e Segurança

- **Confirmação Obrigatória:** Nenhuma ação de escrita (enviar e-mail, arquivar, excluir) é realizada silenciosamente pela IA.
- **Sanitização de HTML:** O corpo HTML dos e-mails passa por rigorosa sanitização removendo `<script>`, `<iframe>`, links `javascript:` e manipuladores `on*` inline para prevenir ataques de Cross-Site Scripting (XSS).
