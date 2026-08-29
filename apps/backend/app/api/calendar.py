from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.calendar import EventCreate, EventUpdate, EventResponse
from app.repositories.base import BaseRepository
from app.models.calendar import CalendarEvent

router = APIRouter()

def get_calendar_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[CalendarEvent]:
    return BaseRepository(CalendarEvent, db)

@router.get("/", response_model=List[EventResponse])
async def get_events(skip: int = 0, limit: int = 100, repo: BaseRepository[CalendarEvent] = Depends(get_calendar_repo)):
    return await repo.get_all(skip, limit)

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_in: EventCreate, repo: BaseRepository[CalendarEvent] = Depends(get_calendar_repo)):
    data = event_in.model_dump()
    return await repo.create(**data)

@router.get("/{id}", response_model=EventResponse)
async def get_event(id: int, repo: BaseRepository[CalendarEvent] = Depends(get_calendar_repo)):
    event = await repo.get_by_id(id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event

@router.put("/{id}", response_model=EventResponse)
async def update_event(id: int, event_in: EventUpdate, repo: BaseRepository[CalendarEvent] = Depends(get_calendar_repo)):
    data = event_in.model_dump(exclude_unset=True)
    event = await repo.update(id, **data)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(id: int, repo: BaseRepository[CalendarEvent] = Depends(get_calendar_repo)):
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return None
