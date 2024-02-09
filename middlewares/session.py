from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy import select

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import CREATOR
from database.models.user import User


async def check_user(session: AsyncSession, user_id: int) -> bool:
    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        return False, False

    if user.is_block and user_id != CREATOR:
        block = True
    else:
        block = False

    if user.is_admin or user_id == CREATOR:
        admin = True
    else:
        admin = False

    return admin, block


class SessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        async with self.sessionmaker() as session:
            user = data['event_from_user']
            admin, block = await check_user(session, user.id)
            data['session'] = session
            data['is_admin'] = admin
            data['is_block'] = block
            return await handler(event, data)
