from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Tuple, Optional
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def _ensure_role(current_user:User , allowed_roles:Tuple
[UserRole,...]) -> User:
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="??? ???? ?????? ??????? ??? ??? ??????"
        )
    return current_user   
 
async def get_current_pool_owner(
    current_user: User = Depends(get_current_active_user)
) -> User:
    return _ensure_role(current_user , (UserRole.POOL_OWNER,))

async def get_current_company_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    return _ensure_role(current_user , (UserRole.COMPANY,))

async def get_current_technician(
    current_user: User = Depends(get_current_active_user)
) -> User:
    return _ensure_role(current_user , (UserRole.TECHNICIAN,))

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except:
        return None