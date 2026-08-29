from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.search import SearchResponse

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search_all(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    # Basic mock search implementation across multiple entities
    results = []
    
    # Needs implementation of text search on Tasks, Expenses, Subjects, Events
    # Returning empty list for now, would be filled with actual results
    
    return {
        "query": q,
        "total": len(results),
        "results": results
    }
