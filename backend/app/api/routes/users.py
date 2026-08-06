from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin, get_current_user
from app.database import get_db
from app.persistence.entities import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(user: Annotated[User, Depends(get_current_user)]):
    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
def list_users(_: Annotated[User, Depends(get_current_admin)], db: Session = Depends(get_db)):
    return [UserResponse.model_validate(user) for user in UserRepository(db).list()]


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdateRequest,
    admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)
    if not user_id.isdigit():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user = repository.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    would_remove_admin = user.role == "admin" and (request.role == "user" or request.is_active is False)
    if would_remove_admin and repository.count_admins() == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="系统至少需要保留一名管理员")
    return UserResponse.model_validate(repository.update(user, role=request.role, is_active=request.is_active))
