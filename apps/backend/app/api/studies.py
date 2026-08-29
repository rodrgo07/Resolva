from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.study import (
    SubjectCreate, SubjectUpdate, SubjectResponse, 
    SessionResponse, SessionCreate, StudySummary
)
from app.services.study_service import StudyService
from app.repositories.study_repository import StudyRepository

router = APIRouter()

def get_study_service(db: AsyncSession = Depends(get_db)) -> StudyService:
    repo = StudyRepository(db)
    return StudyService(repo)

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(skip: int = 0, limit: int = 100, service: StudyService = Depends(get_study_service)):
    return await service.get_all_subjects(skip, limit)

@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(subject: SubjectCreate, service: StudyService = Depends(get_study_service)):
    return await service.create_subject(subject)

@router.get("/subjects/{id}", response_model=SubjectResponse)
async def get_subject(id: int, service: StudyService = Depends(get_study_service)):
    return await service.get_subject(id)

@router.put("/subjects/{id}", response_model=SubjectResponse)
async def update_subject(id: int, subject: SubjectUpdate, service: StudyService = Depends(get_study_service)):
    return await service.update_subject(id, subject)

@router.delete("/subjects/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(id: int, service: StudyService = Depends(get_study_service)):
    await service.delete_subject(id)
    return None

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(subject_id: int = None, service: StudyService = Depends(get_study_service)):
    if subject_id:
        return await service.get_sessions(subject_id)
    return await service.get_all_sessions()

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: SessionCreate, service: StudyService = Depends(get_study_service)):
    return await service.create_session(session_data)

@router.get("/summary", response_model=StudySummary)
async def get_summary(service: StudyService = Depends(get_study_service)):
    return await service.get_summary()
