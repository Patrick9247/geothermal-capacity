from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, request: RegisterRequest) -> UserResponse:
        if self.repository.get_by_username(request.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
        if self.repository.get_by_email(str(request.email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已被注册")
        role = "admin" if self.repository.count() == 0 else "user"
        user = self.repository.create(username=request.username, email=str(request.email), password_hash=hash_password(request.password), role=role)
        return UserResponse.model_validate(user)

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_identifier(request.identifier)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名、邮箱或密码错误")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该用户已被停用")
        return TokenResponse(access_token=create_access_token(str(user.id)), user=UserResponse.model_validate(user))
