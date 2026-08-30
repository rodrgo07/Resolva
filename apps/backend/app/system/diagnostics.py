from typing import Dict, Any, List, Optional
from datetime import datetime

class DiagnosticsService:
    """
    Serviço de Diagnóstico Estruturado e Relatório Sanitizado (Fase 35).
    """

    @classmethod
    def analyze_system_state(cls, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        diagnostics = []
        now = datetime.utcnow().isoformat()

        components = health_data.get("components", {})
        for name, comp in components.items():
            status = comp.get("status")
            if status in ["WARNING", "CRITICAL", "DEGRADED"]:
                diagnostics.append({
                    "code": f"{name.upper()}_{status}",
                    "level": "CRITICAL" if status == "CRITICAL" else "WARNING",
                    "component": name.upper(),
                    "message": comp.get("message", "Anomalia detectada"),
                    "timestamp": now,
                    "recommended_action": comp.get("recommended_action", "Verificar logs do sistema.")
                })

        if not diagnostics:
            diagnostics.append({
                "code": "SYSTEM_OPTIMAL",
                "level": "INFO",
                "component": "CORE",
                "message": "Todos os subsistemas operando em condições ideais.",
                "timestamp": now
            })

        return diagnostics
