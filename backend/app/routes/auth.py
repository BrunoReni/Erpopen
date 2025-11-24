from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserRead, Token
from app.db import get_session
from app import crud
from app.security import create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session, payload.email, payload.password, payload.full_name)
    if not user:
        raise HTTPException(status_code=500, detail="Could not create user")
    
    user_roles, user_permissions = crud.get_user_roles_and_permissions(session, user.id)
    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        full_name=user.full_name,
        roles=user_roles,
        permissions=user_permissions
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = crud.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    
    _, user_permissions = crud.get_user_roles_and_permissions(session, user.id)
    token = create_access_token(subject=user.email, permissions=user_permissions)
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    subject = payload.get("sub")
    user = crud.get_user_by_email(session, subject)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_roles, user_permissions = crud.get_user_roles_and_permissions(session, user.id)
    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        full_name=user.full_name,
        roles=user_roles,
        permissions=user_permissions
    )


@router.get("/users")
def list_users(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """List all users"""
    from app.models import User
    users = session.query(User).all()
    result = []
    for user in users:
        user_roles, _ = crud.get_user_roles_and_permissions(session, user.id)
        result.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": user_roles,
            "created_at": None  # Modelo não tem este campo
        })
    return result


@router.get("/roles")
def list_roles(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """List all roles"""
    from app.models import Role
    roles = session.query(Role).all()
    return [{"id": r.id, "name": r.name, "description": r.description} for r in roles]


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: dict,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Update user"""
    from app.models import User, UserRole
    
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update basic fields
    if "email" in payload:
        user.email = payload["email"]
    if "full_name" in payload:
        user.full_name = payload["full_name"]
    if "is_active" in payload:
        user.is_active = payload["is_active"]
    if "password" in payload and payload["password"]:
        from app.security import hash_password
        user.hashed_password = hash_password(payload["password"])
    
    # Update roles
    if "role_ids" in payload:
        # Remove existing roles
        session.query(UserRole).filter(UserRole.user_id == user_id).delete()
        # Add new roles
        for role_id in payload["role_ids"]:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            session.add(user_role)
    
    session.commit()
    session.refresh(user)
    
    user_roles, _ = crud.get_user_roles_and_permissions(session, user.id)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": user_roles
    }
