# Workflow Conditions Engine (Fase 33)

## 1. Avaliador Seguro
- Sem uso de eval() ou exec().
- Operadores suportados: EQ, NEQ, GT, GTE, LT, LTE, IN, NOT_IN, CONTAINS, NOT_CONTAINS, IS_EMPTY, IS_NOT_EMPTY.
- Operadores Lógicos: AND, OR, NOT com aninhamento arbitrário seguro contra o contexto sanitizado.
