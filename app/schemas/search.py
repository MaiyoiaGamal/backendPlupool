from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SearchHistoryResponse(BaseModel):
    id: int
    search_query: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchSuggestionResponse(BaseModel):
    query: str
    created_at: datetime

