# RESOLVA — Push Notifications Multidispositivo

## 1. Gestão de Tokens Push

- O RESOLVA Mobile registra seu push token (compatível com Expo Notifications, FCM e APNs) via `POST /api/remote/devices/{device_id}/push-token`.
- O token é vinculado ao dispositivo na tabela `push_device_tokens`.
- Ao revogar o acesso do dispositivo no Desktop, os tokens push associados são desativados imediatamente.

---

## 2. Isolamento de Dados

- Os tokens de push notification contêm apenas identificadores de transporte.
- As notificações trafegam com títulos e resumos sanitizados, sem expor chaves de API, senhas ou tokens OAuth.
