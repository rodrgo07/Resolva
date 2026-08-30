# Workflow Security & Permission Layer (Fase 33)

## 1. Princípios Invioláveis
- **Zero Shell / PowerShell / CMD**: Nenhuma instrução arbitrária do SO é permitida.
- **Catálogo Homologado**: Somente ações registradas em workflow_catalog.py podem ser executadas.
- **Detecção de Injeção**: Validador regex contra SQL Injection, script injection e comandos maliciosos.
- **Proteção contra Loops**: Limite máximo de profundidade de disparo (max_trigger_depth = 5) e rate limiting por minuto.
- **Kill Switch**: Interrupção global instantânea de todas as rotinas em caso de emergência.
