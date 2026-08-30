from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.automation.workflow_engine import WorkflowEngine
from app.automation.workflow_templates import WORKFLOW_TEMPLATES
from app.automation.workflow_recommendations import WorkflowRecommendationsEngine
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecutionResponse, WorkflowExecuteRequest,
    WorkflowConfirmationRequest, WorkflowRecommendationResponse,
    WorkflowTemplateResponse
)
from app.core.exceptions import NotFoundError, PermissionError

router = APIRouter(prefix="/workflows", tags=["workflows"])

# ========================================================
# 1. CRUD WORKFLOWS
# ========================================================

@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.list_workflows(status)

@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    req: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.create_workflow(req.model_dump(), created_by="USER")

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    wf = await engine.get_workflow(workflow_id)
    if not wf:
        raise NotFoundError("Workflow não encontrado.")
    return wf

@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str = Path(...),
    req: WorkflowUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.update_workflow(workflow_id, req.model_dump(exclude_unset=True))

@router.delete("/{workflow_id}", status_code=status.HTTP_200_OK)
async def delete_workflow(
    workflow_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    wf = await engine.get_workflow(workflow_id)
    if not wf:
        raise NotFoundError("Workflow não encontrado.")
    await db.delete(wf)
    await db.commit()
    return {"message": "Workflow removido com sucesso."}

# ========================================================
# 2. STATE CONTROLS & EXECUTION
# ========================================================

@router.post("/{workflow_id}/activate", response_model=WorkflowResponse)
async def activate_workflow(
    workflow_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.activate_workflow(workflow_id)

@router.post("/{workflow_id}/pause", response_model=WorkflowResponse)
async def pause_workflow(
    workflow_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.pause_workflow(workflow_id)

@router.post("/{workflow_id}/test", response_model=WorkflowExecutionResponse)
async def test_workflow_dry_run(
    workflow_id: str = Path(...),
    req: WorkflowExecuteRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.execute_workflow(
        workflow_id=workflow_id,
        trigger_source=req.trigger_source,
        device_id=req.device_id,
        dry_run=True,
        context_override=req.context_override
    )

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str = Path(...),
    req: WorkflowExecuteRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.execute_workflow(
        workflow_id=workflow_id,
        trigger_source=req.trigger_source,
        device_id=req.device_id,
        dry_run=req.dry_run,
        context_override=req.context_override
    )

# ========================================================
# 3. CONFIRMATIONS
# ========================================================

@router.post("/confirmations/{confirmation_id}/resolve", response_model=WorkflowExecutionResponse)
async def resolve_confirmation(
    confirmation_id: str = Path(...),
    req: WorkflowConfirmationRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    engine = WorkflowEngine(db)
    return await engine.resolve_confirmation(
        confirmation_id=confirmation_id,
        approved=req.approved,
        device_id=req.device_id
    )

# ========================================================
# 4. TEMPLATES & RECOMMENDATIONS
# ========================================================

@router.get("/catalog/templates", response_model=List[WorkflowTemplateResponse])
async def list_templates():
    return WORKFLOW_TEMPLATES

@router.get("/catalog/recommendations", response_model=List[WorkflowRecommendationResponse])
async def list_recommendations(db: AsyncSession = Depends(get_db)):
    rec_engine = WorkflowRecommendationsEngine(db)
    return await rec_engine.list_recommendations()

@router.post("/catalog/recommendations/{recommendation_id}/accept", response_model=WorkflowRecommendationResponse)
async def accept_recommendation(
    recommendation_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    rec_engine = WorkflowRecommendationsEngine(db)
    rec = await rec_engine.accept_recommendation(recommendation_id)
    if not rec:
        raise NotFoundError("Recomendação não encontrada.")
    return rec

@router.post("/catalog/recommendations/{recommendation_id}/dismiss", response_model=WorkflowRecommendationResponse)
async def dismiss_recommendation(
    recommendation_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    rec_engine = WorkflowRecommendationsEngine(db)
    rec = await rec_engine.dismiss_recommendation(recommendation_id)
    if not rec:
        raise NotFoundError("Recomendação não encontrada.")
    return rec
