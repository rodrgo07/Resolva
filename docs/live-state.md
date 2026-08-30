# Multi-Device Live State Mirroring (Fase 32)

## 1. Visão Geral
O Live State Engine é responsável por manter o estado de atividades em tempo real perfeitamente espelhado entre o Windows Desktop (Tauri + FastAPI) e dispositivos móveis Android / iOS (React Native + Expo).

## 2. Modelos & Sessões Ativas
- **LiveSession**: Representa sessões ativas como Pomodoro, Focus Timer, Active Planning Block e Agent Sessions.
- **Campos**: session_id, type, status (IDLE, RUNNING, PAUSED, COMPLETED, CANCELLED), started_at, paused_at, duration_seconds, remaining_seconds, version, origin_device_id.

## 3. Relógio e Timestamps Confiáveis
Em vez de depender de contadores independentes, a sincronização é calculada com base no timestamp de início (started_at) e na duração estipulada, garantindo tolerância a falhas temporárias de rede.
