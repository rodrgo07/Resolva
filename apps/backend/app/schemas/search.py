from pydantic import BaseModel
from typing import List, Dict, Any

class SearchResult(BaseModel):
    id: int
    type: str
    title: str
    description: str
    match_score: float
    url: str

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
