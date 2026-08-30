# Workflow Execution & Dry Run Simulation (Fase 33)

## 1. Dry Run / Simulação
Permite que o usuário teste qualquer workflow antes de ativá-lo. As condições e parâmetros são validados sem realizar qualquer alteração persistente no banco de dados.

## 2. Retries & Timeouts Controlados
- Retry configurável com backoff exponencial seguro (ex: 5s, 15s, 30s).
- Timeout máximo por workflow (max_runtime_seconds) com cancelamento automático de etapas pendentes se o tempo for excedido.
