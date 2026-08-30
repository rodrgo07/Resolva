# Desktop Release Architecture (Tauri v2)

## 1. Distribuição Windows
- Empacotamento via NSIS / MSI com inicialização em segundo plano no System Tray.
- Error Boundaries globais impedindo quebra da aplicação em exceções de renderização.
