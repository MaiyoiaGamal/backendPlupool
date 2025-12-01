from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, distinct
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.models.search_history import SearchHistory
from app.schemas.search import SearchHistoryResponse

router = APIRouter()

@router.get("/search/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = Query(10, ge=1, le=50, description="عدد النتائج"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    الحصول على تاريخ البحث
    Get search history
    """
    if not current_user:
        return []
    
    # جلب آخر عمليات البحث المميزة (بدون تكرار)
    search_history = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(
        desc(SearchHistory.created_at)
    ).all()
    
    # تحويل النتائج مع إزالة التكرار
    results = []
    seen_queries = set()
    for item in search_history:
        if item.search_query not in seen_queries:
            seen_queries.add(item.search_query)
            results.append(SearchHistoryResponse(
                id=item.id,
                search_query=item.search_query,
                created_at=item.created_at
            ))
            if len(results) >= limit:
                break
    
    return results

