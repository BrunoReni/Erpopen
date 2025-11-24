from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.db import get_session
from app.security import decode_access_token
from app import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Get the current authenticated user"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_permission(required_permission: str):
    """
    Dependency factory that checks if user has specific permission.
    Usage: @router.get("/", dependencies=[Depends(require_permission("users:read"))])
    """
    def permission_checker(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
    ):
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_permissions = payload.get("permissions", [])
        
        # Check for wildcard admin permission
        if "*:*" in user_permissions:
            return True
        
        # Check for specific permission
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {required_permission}"
            )
        
        return True
    
    return permission_checker


def require_any_permission(required_permissions: List[str]):
    """
    Dependency factory that checks if user has ANY of the specified permissions.
    Usage: @router.get("/", dependencies=[Depends(require_any_permission(["users:read", "users:update"]))])
    """
    def permission_checker(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
    ):
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_permissions = payload.get("permissions", [])
        
        # Check for wildcard admin permission
        if "*:*" in user_permissions:
            return True
        
        # Check if user has any of the required permissions
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required one of: {', '.join(required_permissions)}"
            )
        
        return True
    
    return permission_checker
