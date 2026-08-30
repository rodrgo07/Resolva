# Fronteira de Segurança do Frontend

## 1. Regras Invioláveis
- Zero comandos shell / powershell no frontend.
- Zero secrets no bundle Vite ou código TypeScript.
- Toda validação de formulário é apenas UX (a validação autoritativa ocorre no backend via Pydantic).
