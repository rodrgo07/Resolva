from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.automation import AutomationCreate, AutomationUpdate, AutomationResponse, ExecutionResponse
from app.repositories.base import BaseRepository
from app.models.automation import Automation, AutomationExecution
from app.automation.engine import AutomationEngine

router = APIRouter()

def get_automation_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Automation]:
    return BaseRepository(Automation, db)

def get_execution_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[AutomationExecution]:
    return BaseRepository(AutomationExecution, db)

@router.get("/", response_model=List[AutomationResponse])
async def get_automations(skip: int = 0, limit: int = 50, repo: BaseRepository[Automation] = Depends(get_automation_repo)):
    return await repo.get_all(skip, limit)

from app.models.automation import AutomationTrigger, AutomationAction

@router.post("/", response_model=AutomationResponse, status_code=status.HTTP_201_CREATED)
async def create_automation(auto_in: AutomationCreate, db: AsyncSession = Depends(get_db)):
    data = auto_in.model_dump()
    triggers_data = data.pop("triggers", [])
    actions_data = data.pop("actions", [])
    
    auto = Automation(**data)
    db.add(auto)
    await db.commit()
    await db.refresh(auto)
    
    for t in triggers_data:
        trig = AutomationTrigger(automation_id=auto.id, **t)
        db.add(trig)
        
    for a in actions_data:
        act = AutomationAction(automation_id=auto.id, **a)
        db.add(act)
        
    await db.commit()
    await db.refresh(auto)
    return auto

@router.get("/{id}", response_model=AutomationResponse)
async def get_automation(id: int, repo: BaseRepository[Automation] = Depends(get_automation_repo)):
    auto = await repo.get_by_id(id)
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    return auto

@router.put("/{id}", response_model=AutomationResponse)
async def update_automation(id: int, auto_in: AutomationUpdate, repo: BaseRepository[Automation] = Depends(get_automation_repo)):
    data = auto_in.model_dump(exclude_unset=True)
    auto = await repo.update(id, **data)
    if not auto:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    return auto

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(id: int, repo: BaseRepository[Automation] = Depends(get_automation_repo)):
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    return None

@router.post("/{id}/run", response_model=ExecutionResponse)
async def run_automation(id: int, db: AsyncSession = Depends(get_db)):
    engine = AutomationEngine(db)
    return await engine.run_automation(id)

@router.get("/{id}/executions", response_model=List[ExecutionResponse])
async def get_executions(id: int, exec_repo: BaseRepository[AutomationExecution] = Depends(get_execution_repo)):
    all_execs = await exec_repo.get_all(0, 50)
    return [e for e in all_execs if e.automation_id == id]
