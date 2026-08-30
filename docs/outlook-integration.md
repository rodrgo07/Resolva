# Guia de Integração Microsoft 365 / Outlook (Microsoft Graph API) - RESOLVA

Este guia descreve os passos para registrar e configurar o aplicativo **RESOLVA** na **Microsoft Identity Platform (Azure Entra ID)** para sincronização de e-mails via **Microsoft Graph API**.

---

## 1. Visão Geral da Arquitetura

O `OutlookProvider` implementa a interface comum `EmailProvider`:

- **Protocolo:** OAuth 2.0 Authorization Code Flow com PKCE para Desktop / Public Clients.
- **API:** Microsoft Graph API v1.0 (`https://graph.microsoft.com/v1.0`).
- **Sanitização & Normalização:** Todas as mensagens retornam como instâncias de `NormalizedEmail`, aplicando a mesma política de segurança e categorização por IA do RESOLVA.
- **Resiliência:** Tratamento nativo de rate limiting (`HTTP 429` com cabeçalho `Retry-After`) e sinalização de expiração de credenciais (`REAUTH_REQUIRED`).

---

## 2. Configuração no Portal do Azure (Microsoft Entra ID)

1. Acesse o [Portal do Azure - Registros de aplicativo](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
2. Clique em **+ Novo registro** (*New registration*):
   - **Nome:** `Resolva Desktop`
   - **Tipos de conta com suporte:** *Contas em qualquer diretório organizacional (Qualquer diretório do Microsoft Entra ID - Multilocatário) e contas pessoais da Microsoft (por exemplo, Skype, Xbox)*.
   - **URI de Redirecionamento (opcional):** Selecione **Aplicativo público/móvel (área de trabalho e móvel)** e insira `http://localhost:8700/api/emails/connect/callback`.
3. Clique em **Registrar**.
4. Na página de **Visão Geral** do aplicativo, copie o **ID do Aplicativo (cliente)** (*Application (client) ID*).
5. Vá em **Permissões de API > + Adicionar uma permissão > Microsoft Graph > Permissões delegadas**:
   - `User.Read` (ler perfil básico do usuário)
   - `Mail.Read` (ler e-mails)
   - `Mail.ReadWrite` (atualizar status de lido e arquivamento)
   - `offline_access` (obter refresh token para sincronização contínua)
6. Configure as variáveis no seu `.env`:
   ```env
   OUTLOOK_CLIENT_ID=seu_application_client_id_aqui
   OUTLOOK_TENANT_ID=common
   ```

---

## 3. Segurança e Tokens

- **Armazenamento:** Tokens do Microsoft Graph são armazenados exclusivamente no **Cofre Windows DPAPI / Vault** do usuário (`%APPDATA%\Resolva\credentials\`).
- **Nenhum Dado Sensível no SQLite:** Apenas o identificador da conta, e-mail e carimbos de sincronização residem no banco local.
- **Sem Envio Automático:** Qualquer resposta ou arquivamento exige confirmação explícita na interface do usuário.

---

## 4. Troubleshooting

- **Erro `REAUTH_REQUIRED`:** Caso a senha da conta Microsoft seja alterada ou o consentimento revogado, o RESOLVA solicitará a reconexão na tela de configurações sem perder os e-mails sincronizados anteriormente.
- **Rate Limit (`HTTP 429`):** O provedor aguarda automaticamente o intervalo retornado no cabeçalho `Retry-After` antes de prosseguir.
