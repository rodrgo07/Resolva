from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.search import SearchResponse, SearchResult
from app.models.task import Task
from app.models.finance import Expense
from app.models.study import StudySubject
from app.models.calendar import CalendarEvent

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search_all(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    search_term = f"%{q.lower()}%"
    results = []

    # 1. Search Tasks
    tasks_query = select(Task).where(
        (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
    ).limit(5)
    tasks_res = await db.execute(tasks_query)
    for t in tasks_res.scalars().all():
        results.append(
            SearchResult(
                id=t.id,
                type="task",
                title=t.title,
                description=t.description or f"Tarefa ({t.priority})",
                match_score=1.0,
                url="/tasks"
            )
        )

    # 2. Search Expenses/Finances
    exp_query = select(Expense).where(
        (Expense.description.ilike(search_term)) | (Expense.notes.ilike(search_term))
    ).limit(5)
    exp_res = await db.execute(exp_query)
    for e in exp_res.scalars().all():
        results.append(
            SearchResult(
                id=e.id,
                type="finance",
                title=e.description,
                description=f"R$ {e.amount:.2f} ({e.type})",
                match_score=0.9,
                url="/finances"
            )
        )

    # 3. Search Study Subjects
    sub_query = select(StudySubject).where(
        (StudySubject.name.ilike(search_term)) | (StudySubject.description.ilike(search_term))
    ).limit(5)
    sub_res = await db.execute(sub_query)
    for s in sub_res.scalars().all():
        results.append(
            SearchResult(
                id=s.id,
                type="study",
                title=s.name,
                description=s.description or f"Progresso: {s.progress}%",
                match_score=0.95,
                url="/studies"
            )
        )

    # 4. Search Calendar Events
    ev_query = select(CalendarEvent).where(
        (CalendarEvent.title.ilike(search_term)) | (CalendarEvent.description.ilike(search_term))
    ).limit(5)
    ev_res = await db.execute(ev_query)
    for ev in ev_res.scalars().all():
        results.append(
            SearchResult(
                id=ev.id,
                type="calendar",
                title=ev.title,
                description=ev.description or "Evento agendado",
                match_score=0.85,
                url="/calendar"
            )
        )

    return SearchResponse(
        query=q,
        total=len(results),
        results=results
    )
