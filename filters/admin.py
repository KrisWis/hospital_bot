from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class UserAdminFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, is_admin: bool) -> bool:
        if is_admin:
            return True
        else:
            text = '❌ У вас нет доступа к этой возможности!'
            if isinstance(message, Message):
                await message.answer(text=text)
            else:
                await message.answer(text=text, show_alert=True)
            return False