from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.bot import Bot
from backend.app.schemas.bot import BotCreate
from backend.app.core.security import generate_bot_token

class BotService:
    @staticmethod
    async def create_bot(db: AsyncSession, bot_in: BotCreate) -> Bot:
        # Check if username exists
        res = await db.execute(select(Bot).where(Bot.username == bot_in.username))
        if res.scalar_one_or_none():
            raise ValueError(f"Bot with username @{bot_in.username} already exists")

        # Create record without token first to get auto-incremented ID (or use random ID)
        bot = Bot(
            name=bot_in.name,
            username=bot_in.username.lstrip("@"),
            token="placeholder",
            description=bot_in.description or "",
            avatar=bot_in.avatar or ""
        )
        db.add(bot)
        await db.commit()
        await db.refresh(bot)

        # Generate unique token with bot_id prefix
        bot.token = generate_bot_token(bot.id)
        await db.commit()
        await db.refresh(bot)
        return bot

    @staticmethod
    async def get_all_bots(db: AsyncSession) -> List[Bot]:
        res = await db.execute(select(Bot).order_by(Bot.id.desc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_bot_by_id(db: AsyncSession, bot_id: int) -> Optional[Bot]:
        res = await db.execute(select(Bot).where(Bot.id == bot_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def delete_bot(db: AsyncSession, bot_id: int) -> bool:
        bot = await BotService.get_bot_by_id(db, bot_id)
        if not bot:
            return False
        await db.delete(bot)
        await db.commit()
        return True

bot_service = BotService()
