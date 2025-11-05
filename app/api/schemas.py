from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str

class MovieResponse(BaseModel):
    id: int
    title: str
    year: Optional[int]
    overview: Optional[str]
    genres: List[str]
    avg_rating: Optional[float]
    cast: List[Dict[str, str]]
    directors: List[str]

class ChatResponse(BaseModel):
    response: str
    movies: List[MovieResponse]
    intent: str
    params: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    message: str