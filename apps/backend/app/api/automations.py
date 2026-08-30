from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.automation import Automation, AutomationTrigger, AutomationAction, AutomationExecution
from app.schemas.automation import (
    AutomationCreate, AutomationUpdate, AutomationResponse,
    ExecutionResponse, AutomationDraft
)
from app.automation.engine import AutomationEngine
from app.automation.kill_switch import (
    is_kill_switch_active, activate_kill_switch, deactivate_kill_switch
)
from app.automation.permissions import AutomationPermissionService

router = APIRouter()

@router.get("/", response_model=List[AutomationResponse])
async def list_automations(db: AsyncSession = Depends(get_db)):
    query = select(Automation).options(
        selectinload(Automation.triggers),
        selectinload(Automation.actions)
    ).order_by(Automation.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/templates")
async def get_templates():
    """Retorna templates de rotinas pré-configuradas prontas para uso"""
    return [
        {
            "id": "tpl_morning",
            "name": "Rotina da Manhã",
            "description": "Abre o ambiente de desenvolvimento, consulta tarefas e e-mails prioritários.",
            "trigger": {"type": "SCHEDULE", "config": {"time": "08:00", "days": [0, 1, 2, 3, 4]}},
            "actions": [
                {"type": "OPEN_APPLICATION", "config": {"app_name": "vscode"}},
                {"type": "SHOW_AGENT_MESSAGE", "config": {"message": "Bom dia! Suas tarefas prioritárias e e-mails estão prontos no Dashboard."}},
                {"type": "SYNC_EMAIL", "config": {}}
            ],
            "risk_level": "HIGH",
            "requires_confirmation": True
        },
        {
            "id": "tpl_study",
            "name": "Foco & Sessão de Estudos",
            "description": "Prepara ambiente focado, bloqueia notificações e inicia Pomodoro de 25 minutos.",
            "trigger": {"type": "MANUAL", "config": {}},
            "actions": [
                {"type": "CREATE_NOTIFICATION", "config": {"title": "Modo Estudo Ativado", "message": "Iniciando sessão Pomodoro focada."}},
                {"type": "START_STUDY_SESSION", "config": {"duration_minutes": 25, "subject_id": 1}}
            ],
            "risk_level": "LOW",
            "requires_confirmation": False
        },
        {
            "id": "tpl_weekly",
            "name": "Revisão Semanal",
            "description": "Gera o resumo de tarefas concluídas, gastos da semana e horas estudadas.",
            "trigger": {"type": "SCHEDULE", "config": {"time": "20:00", "days": [6]}},
            "actions": [
                {"type": "GENERATE_WEEKLY_SUMMARY", "config": {}},
                {"type": "CREATE_NOTIFICATION", "config": {"title": "Revisão Semanal Pronta", "message": "Seu resumo da semana foi gerado pelo Resolva Agent."}}
            ],
            "risk_level": "LOW",
            "requires_confirmation": False
        }
    ]

@router.get("/kill-switch/status")
async def get_kill_switch():
    return {"is_active": is_kill_switch_active()}

@router.post("/kill-switch/activate")
async def trigger_kill_switch():
    activate_kill_switch()
    return {"status": "success", "message": "Kill Switch ativado. Todas as automações foram pausadas globalmente.", "is_active": True}

@router.post("/kill-switch/deactivate")
async def untrigger_kill_switch():
    deactivate_kill_switch()
    return {"status": "success", "message": "Kill Switch desativado. Automações reestabelecidas.", "is_active": False}

@router.post("/", response_model=AutomationResponse, status_code=status.HTTP_201_CREATED)
async def create_automation(payload: AutomationCreate, db: AsyncSession = Depends(get_db)):
    automation = Automation(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
        icon=payload.icon or "zap"
    )
    db.add(automation)
    await db.commit()
    await db.refresh(automation)

    for trig in payload.triggers:
        t = AutomationTrigger(automation_id=automation.id, type=trig.type, config=trig.config)
        db.add(t)

    for idx, act in enumerate(payload.actions):
        a = AutomationAction(
            automation_id=automation.id,
            type=act.type,
            config=act.config,
            sort_order=act.sort_order if act.sort_order is not None else idx,
            requires_confirmation=act.requires_confirmation
        )
        db.add(a)

    await db.commit()

    query = select(Automation).options(
        selectinload(Automation.triggers),
        selectinload(Automation.actions)
    ).where(Automation.id == automation.id)
    res = await db.execute(query)
    return res.scalars().first()

@router.get("/{id}", response_model=AutomationResponse)
async def get_automation(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Automation).options(
        selectinload(Automation.triggers),
        selectinload(Automation.actions)
    ).where(Automation.id == id)
    res = await db.execute(query)
    auto = res.scalars().first()
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    return auto

@router.put("/{id}", response_model=AutomationResponse)
async def update_automation(id: int, payload: AutomationUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Automation).options(
        selectinload(Automation.triggers),
        selectinload(Automation.actions)
    ).where(Automation.id == id)
    res = await db.execute(query)
    auto = res.scalars().first()
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")

    if payload.name is not None: auto.name = payload.name
    if payload.description is not None: auto.description = payload.description
    if payload.is_active is not None: auto.is_active = payload.is_active
    if payload.icon is not None: auto.icon = payload.icon

    await db.commit()
    await db.refresh(auto)
    return auto

@router.post("/{id}/toggle", response_model=AutomationResponse)
async def toggle_automation(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Automation).where(Automation.id == id)
    res = await db.execute(query)
    auto = res.scalars().first()
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    auto.is_active = not auto.is_active
    await db.commit()
    await db.refresh(auto)
    return auto

@router.delete("/{id}")
async def delete_automation(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Automation).where(Automation.id == id)
    res = await db.execute(query)
    auto = res.scalars().first()
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    await db.delete(auto)
    await db.commit()
    return {"status": "deleted", "id": id}

@router.post("/{id}/run", response_model=ExecutionResponse)
async def run_automation(
    id: int,
    confirmed: bool = Query(False, description="Confirmação para ações de alto risco"),
    db: AsyncSession = Depends(get_db)
):
    engine = AutomationEngine(db)
    return await engine.run_automation(id, is_confirmed=confirmed)

@router.get("/{id}/executions", response_model=List[ExecutionResponse])
async def get_executions(id: int, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    query = select(AutomationExecution).where(AutomationExecution.automation_id == id).order_by(AutomationExecution.started_at.desc()).offset(skip).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())
