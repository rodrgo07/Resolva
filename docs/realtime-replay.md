# Realtime Event Replay & State Resync (Fase 32)

## 1. Sequência Monotônica
Todos os eventos transmitidos pelo EventBus e WebSocket possuem uma sequência estritamente crescente (sequence: int).

## 2. Recuperação Pós-Queda de Rede
Ao reconectar, o cliente móvel ou desktop envia o parâmetro events_after=SEQ_LOCAL. O endpoint GET /api/realtime/events retorna todos os deltas perdidos durante a desconexão. Se a lacuna for muito extensa, o cliente aciona o GET /api/realtime/state para reconstrução íntegra do estado global.
