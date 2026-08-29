from typing import List, Dict, Any
from app.repositories.study_repository import StudyRepository
from app.schemas.study import SubjectCreate, SubjectUpdate, SessionCreate
from app.models.study import StudySubject, StudySession
from app.core.exceptions import NotFoundError

class StudyService:
    def __init__(self, study_repo: StudyRepository):
        self.study_repo = study_repo

    async def get_all_subjects(self, skip: int = 0, limit: int = 100) -> List[StudySubject]:
        return await self.study_repo.get_all(skip=skip, limit=limit)

    async def get_subject(self, id: int) -> StudySubject:
        subject = await self.study_repo.get_by_id(id)
        if not subject:
            raise NotFoundError(f"Study subject with ID {id} not found")
        return subject

    async def create_subject(self, data: SubjectCreate) -> StudySubject:
        return await self.study_repo.create(**data.model_dump(exclude_unset=True))

    async def update_subject(self, id: int, data: SubjectUpdate) -> StudySubject:
        await self.get_subject(id)
        return await self.study_repo.update(id, **data.model_dump(exclude_unset=True))

    async def delete_subject(self, id: int) -> bool:
        await self.get_subject(id)
        return await self.study_repo.delete(id)
        
    async def create_session(self, data: SessionCreate) -> StudySession:
        return await self.study_repo.create_session(data.model_dump(exclude_unset=True))

    async def get_all_sessions(self, limit: int = 50) -> List[StudySession]:
        return await self.study_repo.get_all_sessions(limit)

    async def get_sessions(self, subject_id: int) -> List[StudySession]:
        return await self.study_repo.get_sessions_by_subject(subject_id)

    async def get_summary(self) -> Dict[str, Any]:
        return await self.study_repo.get_study_summary()
