from typing import List, Optional
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        user_id = user_in.id or random.randint(100000, 999999)
        # Check if ID exists
        res = await db.execute(select(User).where(User.id == user_id))
        if res.scalar_one_or_none():
            user_id = random.randint(100000, 999999)

        user = User(
            id=user_id,
            first_name=user_in.first_name,
            last_name=user_in.last_name or "",
            username=user_in.username or "",
            avatar=user_in.avatar or "",
            is_bot=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[User]:
        res = await db.execute(select(User).order_by(User.id.asc()))
        users = list(res.scalars().all())
        if not users:
            # Create a default user if none exist
            default_user = User(
                id=10001,
                first_name="Студент",
                last_name="Python",
                username="student_dev",
                avatar="",
                is_bot=False
            )
            db.add(default_user)
            await db.commit()
            await db.refresh(default_user)
            return [default_user]
        return users

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        res = await db.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

user_service = UserService()
