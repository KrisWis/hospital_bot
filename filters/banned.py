from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class UserBannedFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, is_block: bool) -> bool:
        if not is_block:
            return True
        else:
            text = '❌ Ваш аккаунт заблокирован в боте!'
            if isinstance(message, Message):
                await message.answer(text=text)
            else:
                await message.answer(text=text, show_alert=True)
            return False
