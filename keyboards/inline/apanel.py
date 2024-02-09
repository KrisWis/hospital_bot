from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbackdata import UserInfoData, SetRole, SetPosition


def main_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text='👥 Пользователи', callback_data='GetUsers')
    builder.button(text='📂 Скачать базу', callback_data='GetUsersBase')
    builder.button(text='📨 Рассылка', callback_data='GetMessage')
    builder.button(text='🟢 Обновить информацию', callback_data='APanelRefresh')
    builder.button(text='📌 Главное меню', callback_data='GetStart')

    return builder.adjust(2, 1, 1, 1).as_markup()


def user_info(is_block, is_admin, user_id):
    builder = InlineKeyboardBuilder()

    if is_block:
        builder.button(text='🟢 Разблокировать', callback_data=UserInfoData(user_id=user_id, action='unblock'))
    else:
        builder.button(text='🔴 Заблокировать', callback_data=UserInfoData(user_id=user_id, action='block'))

    if is_admin:
        builder.button(text='🔴 Снять администратора', callback_data=UserInfoData(user_id=user_id, action='unadmin'))
    else:
        builder.button(text='🟢 Назначить администратором', callback_data=UserInfoData(user_id=user_id, action='admin'))

    builder.button(text='🌟 Выдать роль', callback_data=UserInfoData(user_id=user_id, action='role'))
    builder.button(text='✍️ Личные данные', callback_data=UserInfoData(user_id=user_id, action='info'))

    builder.button(text='🔙 В панель управления', callback_data='GetAPanel')

    return builder.adjust(2, 2, 1).as_markup()


def return_apanel():
    builder = InlineKeyboardBuilder()

    builder.button(text='🔙 В панель управления', callback_data='GetAPanel')

    return builder.adjust(1).as_markup()


def set_data(user_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='✍️ Личные данные', callback_data=UserInfoData(user_id=user_id, action='info'))
    builder.button(text='🔙 В панель управления', callback_data='GetAPanel')

    return builder.adjust(1).as_markup()


def message_url():
    builder = InlineKeyboardBuilder()

    builder.button(text='✅ Да', callback_data='GetMessageUrlYes')
    builder.button(text='❌ Нет', callback_data='GetMessageUrlNo')

    return builder.adjust(2).as_markup()


def message_kb(name, url):
    builder = InlineKeyboardBuilder()

    builder.button(text=name, url=url)

    return builder.adjust(1).as_markup()


def set_role(user_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='👩‍⚕️ Ассистент', callback_data=SetRole(user_id=user_id, role='assistant'))
    builder.button(text='👨‍⚕️ Врач', callback_data=SetRole(user_id=user_id, role='doctor'))
    builder.button(text='🧑‍⚕️ Старшая медсестра', callback_data=SetRole(user_id=user_id, role='nurse'))
    builder.button(text='❌ Без роли', callback_data=SetRole(user_id=user_id, role='none'))
    builder.button(text='🔙 В панель управления', callback_data='GetAPanel')

    return builder.adjust(2, 2, 1).as_markup()


def get_position():
    builder = InlineKeyboardBuilder()

    builder.button(text='Терапия', callback_data=SetPosition(type='Терапия'))
    builder.button(text='Ортопедия', callback_data=SetPosition(type='Ортопедия'))
    builder.button(text='Ортодонтия', callback_data=SetPosition(type='Ортодонтия'))
    builder.button(text='Хирургия', callback_data=SetPosition(type='Хирургия'))
    builder.button(text='Нет', callback_data=SetPosition(type='Нет'))

    return builder.adjust(2).as_markup()


def return_user_search():
    builder = InlineKeyboardBuilder()

    builder.button(text='🔙 Далее', callback_data='GetUsers')

    return builder.adjust(1).as_markup()
