# Multi-Device Sync Architecture (Fase 32)

## 1. Fluxo Bidirecional
- **Desktop -> Mobile**: WebSocket (/api/remote/ws) + EventBus + Push Notifications.
- **Mobile -> Desktop**: Remote Commands homologados (/api/remote/commands) + Live State Actions (/api/realtime/state/action) + Delta Sync (/api/realtime/conflicts).

## 2. Segurança e Permission Layer
- Zero Shell / Zero PowerShell / Zero CMD.
- Sem tráfego de senhas ou tokens OAuth.
- Idempotência em todas as operações remotas.
