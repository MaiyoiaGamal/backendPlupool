from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse ,UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    الحصول على بيانات المستخدم الحالي
    Get current user profile
    """
    # إضافة country_code إذا لم يكن موجوداً
    if not hasattr(current_user, 'country_code') or current_user.country_code is None:
        current_user.country_code = '+20'  # Default to Egypt
    return current_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = Query("created_at", description="الترتيب حسب: created_at, id, full_name"),
    order: Optional[str] = Query("desc", description="ترتيب: asc أو desc"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة المستخدمين مع إمكانية الترتيب حسب تاريخ الإنشاء
    Get list of users with sorting by creation date (for admin)
    """
    query = db.query(User)
    
    # الترتيب حسب الحقل المحدد
    if sort_by == "created_at":
        query = query.order_by(desc(User.created_at) if order == "desc" else asc(User.created_at))
    elif sort_by == "id":
        query = query.order_by(desc(User.id) if order == "desc" else asc(User.id))
    elif sort_by == "full_name":
        query = query.order_by(desc(User.full_name) if order == "desc" else asc(User.full_name))
    else:
        # افتراضي: الترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
        query = query.order_by(desc(User.created_at))
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على بيانات مستخدم محدد
    Get specific user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث بيانات مستخدم محدد (يجب أن يكون المستخدم هو نفسه أو مسؤول)
    Update a specific user (only self or admin allowed)
    """
    # 🔒 Authorization: only allow user to update their own profile (extend later for admin)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مسموح لك بتحديث بيانات هذا المستخدم"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    حذف مستخدم محدد (يجب أن يكون المستخدم هو نفسه أو مسؤول)
    Delete a specific user (only self or admin allowed)
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مسموح لك بحذف هذا المستخدم"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    db.delete(user)
    db.commit()
    return  # 204 No Content