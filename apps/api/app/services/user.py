"""User service"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash, verify_password


class UserService:
    """Service for user business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.repository.get_by_email(email)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return await self.repository.get(user_id)

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        return await self.repository.create(db_user)

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        return await self.repository.update(user_id, db_user)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    return await UserService(db).get_by_email(email)


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    return await UserService(db).get_by_id(user_id)


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    return await UserService(db).create(user_data)


async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate) -> Optional[User]:
    return await UserService(db).update(user_id, user_data)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    return await UserService(db).authenticate(email, password)
