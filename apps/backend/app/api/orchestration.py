from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.automation.orchestration_engine import OrchestrationEngine
from app.automation.workflow_selector import WorkflowSelector
from app.schemas.orchestration import (
    OrchestrationRunRequest, OrchestrationRunResponse,
    WorkflowCandidate, WorkflowExplanationResponse,
    WorkflowFeedbackCreate, WorkflowFeedbackResponse,
    OrchestrationMetricsResponse
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

# ========================================================
# 1. STATUS & RECOMMENDATIONS
# ========================================================

@router.get("/status")
async def get_orchestration_status(db: AsyncSession = Depends(get_db)):
    engine = OrchestrationEngine(db)
    return await engine.get_status()

@router.get("/recommendations", response_model=List[WorkflowCandidate])
async def get_workflow_recommendations(db: AsyncSession = Depends(get_db)):
    selector = WorkflowSelector(db)
    return await selector.evaluate_candidates()

@router.get("/workflows/next", response_model=Optional[WorkflowCandidate])
async def get_next_recommended_workflow(db: AsyncSession = Depends(get_db)):
    selector = WorkflowSelector(db)
    candidates = await selector.evaluate_candidates()
    return candidates[0] if candidates else None

# ========================================================
# 2. RUNS, SIMULATION & CHAINS
# ========================================================

@router.post("/simulate")
async def simulate_orchestration(
    req: OrchestrationRunRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = OrchestrationEngine(db)
    return await engine.plan_and_simulate(
        workflow_ids=req.workflow_ids,
        context_override=req.context_override
    )

@router.post("/run", response_model=OrchestrationRunResponse, status_code=status.HTTP_201_CREATED)
async def run_orchestration(
    req: OrchestrationRunRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = OrchestrationEngine(db)
    return await engine.run_orchestration(
        trigger_type=req.trigger_type,
        trigger_source=req.trigger_source,
        device_id=req.device_id,
        is_dry_run=req.is_dry_run,
        workflow_ids=req.workflow_ids,
        context_override=req.context_override,
        idempotency_key=req.idempotency_key
    )

@router.get("/runs", response_model=List[OrchestrationRunResponse])
async def list_orchestration_runs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    engine = OrchestrationEngine(db)
    return await engine.list_runs(limit=limit)

@router.get("/runs/{run_id}", response_model=OrchestrationRunResponse)
async def get_orchestration_run(
    run_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    engine = OrchestrationEngine(db)
    run = await engine.get_run(run_id)
    if not run:
        raise NotFoundError("Orquestração não encontrada.")
    return run

# ========================================================
# 3. FEEDBACK & EXPLANATIONS
# ========================================================

@router.post("/feedback", response_model=WorkflowFeedbackResponse)
async def register_feedback(
    req: WorkflowFeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    engine = OrchestrationEngine(db)
    return await engine.register_feedback(
        workflow_id=req.workflow_id,
        user_action=req.user_action,
        run_id=req.orchestration_run_id,
        reason=req.reason,
        device_id=req.device_id
    )
