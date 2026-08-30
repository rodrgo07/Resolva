# RESOLVA — Pareamento Seguro entre Desktop e Mobile

## 1. Fluxo de Handshake

```
┌─────────────────┐                                  ┌─────────────────┐
│ RESOLVA Desktop │                                  │ RESOLVA Mobile  │
└────────┬────────┘                                  └────────┬────────┘
         │                                                    │
         │ 1. Solicita novo pareamento                       │
         │    (Gera code 6 dígitos + nonce)                  │
         │                                                    │
         │ 2. Exibe Código/QR (5 min exp)                     │
         │───────────────────────────────────────────────────>│
         │                                                    │ 3. Usuário digita código
         │                                                    │    ou escaneia sessão
         │ 4. POST /api/devices/pair/complete                 │
         │<───────────────────────────────────────────────────│
         │                                                    │
         │ 5. Valida nonce, expiração e status PENDING        │
         │    Marca request como CLAIMED (Uso único)          │
         │    Gera Device ID, session_token e refresh_token   │
         │                                                    │
         │ 6. Retorna Tokens Seguros + Desktop Status         │
         │───────────────────────────────────────────────────>│
         │                                                    │
         │ 7. Ambos os nós conectados à Sync Layer            │
         │                                                    │
```

---

## 2. Parâmetros e Proteção Criptográfica

1. **Uso Único (*Single-Use*)**: Assim que a requisição de pareamento é aceita, seu status muda para `CLAIMED`. Qualquer tentativa subsequente de reutilização é rejeitada com código 422.
2. **Janela de Expiração Estrita**: Cada código gerado é válido por exatamente 5 minutos.
3. **Isolamento de Credenciais**: O handshake jamais transita senhas mestras, chaves DPAPI ou tokens de provedores como Google OAuth e Microsoft OAuth.
