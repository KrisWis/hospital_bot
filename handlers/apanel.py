import datetime
import json
import logging
import os

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from keyboards.inline import apanel as inline
from config import folder_path, CREATOR
from utils.callbackdata import UserInfoData, SetRole, SetPosition
from utils.state import APanelState
from database.models.jobs import Jobs
from sqlalchemy import select, extract, and_
import csv

doctor_price = {
    'Терапия': 300,
    'Ортопедия': 300,
    'Ортодонтия': 300,
    'Хирургия': 330,
}


async def apanel_menu_text(session: AsyncSession, bot: Bot):
    me = await bot.get_me()

    total_size = 0
    for path, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(path, file)
            total_size += os.path.getsize(file_path)
    folder_size_mb = total_size / (1024 * 1024)

    total_users = (await session.execute(select(func.count()).select_from(User))).scalar()
    total_blocked = (await session.execute(select(func.count()).select_from(User).where(User.is_block == True))).scalar()
    total_admins = (await session.execute(select(func.count()).select_from(User).where(User.is_admin == True))).scalar()

    text = (f'<b><a href="https://static.tildacdn.com/tild3365-3263-4766-b663-336234653965/orig.gif">🤖</a> '
            f'Панель управления ботом - @{me.username}</b>\n'
            f'╔ Версия панели управления: <b>1.0.0</b>\n'
            f'╠ Дата последнего релиза: <b>21.01.2024</b>\n'
            f'🗂 Размер папки с ботом: <b>{folder_size_mb:.2f} Мб.</b>\n'
            f'👥 Всего пользователей: <b>{total_users} чел.</b>\n'
            f'❌ Заблокировано: <b>{total_blocked} чел.</b>\n'
            f'👤 Администраторов: <b>{total_admins} чел.</b>')

    return text


async def user_info(user: User):
    if user.id == CREATOR:
        creator = '\n\n<b>💎 Разработчик бота</b>'
    else:
        creator = ''
    try:
        seniority = datetime.datetime.now() - user.seniority
        seniority = seniority.days
    except:
        seniority = 0
    text = (f'<b>Информация о пользователе</b>\n\n'
            f'╔ ID: <code>{user.id}</code>\n'
            f'╠ Username: @{user.username}\n'
            f'╠ Имя: <b>{user.full_name}</b>\n'
            f'╚ Дата регистрации: <b>{user.register_date.strftime("%d.%m.%Y %H:%M")}</b>\n\n'
            f'❌ Заблокирован: <b>{"Да" if user.is_block else "Нет"}</b>\n'
            f'👤 Администратор: <b>{"Да" if user.is_admin else "Нет"}</b>{creator}\n'
            f'👩‍⚕️ Ассистент: <b>{"Да" if user.is_assistant else "Нет"}</b>\n'
            f'👨‍⚕️ Врач: <b>{"Да" if user.is_doctor else "Нет"}</b>\n'
            f'🧑‍⚕️ Старшая медсестра: <b>{"Да" if user.is_nurse else "Нет"}</b>\n\n'
            f'╔ ФИО: <b>{user.fio}</b>\n'
            f'╠ Номер телефона: <b>{user.phone}</b>\n'
            f'╠ Должность: <b>{user.position}</b>\n'
            f'╠ Стаж: <b>{seniority} дн.</b>\n'
            f'╚ Расчет в текущем месяце: <b>{user.calculation} руб.</b>')
    keyboard = inline.user_info(user.is_block, user.is_admin, user.id)

    return text, keyboard


async def get_apanel(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await callback.message.delete()
    text = await apanel_menu_text(session, bot)
    keyboard = inline.main_menu()
    await callback.message.answer(text=text, reply_markup=keyboard)


async def apanel_refresh(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    text = await apanel_menu_text(session, bot)
    keyboard = inline.main_menu()
    try:
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    except:
        await callback.answer()


async def get_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    text = 'Для просмотра информации о пользователе отправьте его <b>user id</b> или <b>username</b>.'
    keyboard = inline.return_apanel()
    message = await callback.message.answer(text=text, reply_markup=keyboard)
    await state.set_data({'message_id': message.message_id})
    await state.set_state(APanelState.wait_user)


async def select_user(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data.get('message_id'))

    if message.content_type != ContentType.TEXT:
        text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
        keyboard = inline.return_apanel()
        msg = await message.answer(text=text, reply_markup=keyboard)
        return await state.set_data({'message_id': msg.message_id})

    if message.text[0] == '@':
        user_identifier = message.text[1:]
    else:
        user_identifier = message.text

    select_username = (await session.execute(select(User).where(User.username == user_identifier))).scalar_one_or_none()
    select_id = (await session.execute(select(User).where(User.id == user_identifier))).scalar_one_or_none()

    if not select_username and not select_id:
        text = f'❌ Пользователь <b>{user_identifier}</b> не найден в базе. Повторите ввод!'
        return await message.answer(text=text)

    if select_username:
        user = select_username
    else:
        user = select_id

    text, keyboard = await user_info(user)
    await message.answer(text=text, reply_markup=keyboard)
    await state.clear()


async def edit_user(callback: CallbackQuery, callback_data: UserInfoData, session: AsyncSession, bot: Bot, state: FSMContext):
    user = (await session.execute(select(User).where(User.id == callback_data.user_id))).scalar_one()
    if callback_data.action == 'role':
        await callback.message.delete()
        if user.is_assistant:
            role = '👩‍⚕️ Ассистент'
        elif user.is_doctor:
            role = '👨‍⚕️ Врач'
        elif user.is_nurse:
            role = '🧑‍⚕️ Старшая медсестра'
        else:
            role = '❌ Без роли'
        text = (f'Текущая роль пользователя: <b>{role}</b>\n\n'
                f'Выберите какую роль установить.')
        keyboard = inline.set_role(user.id)
        return await callback.message.answer(text=text, reply_markup=keyboard)

    if callback_data.action == 'info':
        await callback.message.delete()
        text = ('Введите Фамилию Имя Отчество.\n'
                f'* Предыдущее значение: {user.fio}')
        await state.set_data({'user_id': callback_data.user_id})
        await state.set_state(APanelState.wait_fio)
        return await callback.message.answer(text=text)

    if callback_data.user_id == callback.from_user.id:
        text = '❌ Вы не можете выполнять данные действия для своего профиля!'
        return await callback.answer(text=text, show_alert=True)

    if callback_data.user_id == CREATOR:
        text = '❌ Вы не можете выполнять данные действия для разработчика бота!'
        return await callback.answer(text=text, show_alert=True)

    if callback_data.action == 'unblock':
        user.is_block = False
        text = f'✅ Пользователь {callback_data.user_id} (@{user.username}) разблокирован!'
        text_user = ('<b>💡 Уведомление</b>\n\n'
                     f'Администратор <b>{callback.from_user.id}</b> (@{callback.from_user.username}) снял вам блокировку!')
        logging.info(msg=f'Administrator {callback.from_user.id} unblocking {callback_data.user_id}')
    elif callback_data.action == 'block':
        user.is_block = True
        text = f'✅ Пользователь {callback_data.user_id} (@{user.username}) заблокирован!'
        text_user = ('<b>💡 Уведомление</b>\n\n'
                     f'Администратор <b>{callback.from_user.id}</b> (@{callback.from_user.username}) выдал вам блокировку!')
        logging.info(msg=f'Administrator {callback.from_user.id} blocking {callback_data.user_id}')
    elif callback_data.action == 'unadmin':
        user.is_admin = False
        text = f'✅ Пользователю {callback_data.user_id} (@{user.username}) сняты права администратора!'
        text_user = ('<b>💡 Уведомление</b>\n\n'
                     f'Администратор <b>{callback.from_user.id}</b> (@{callback.from_user.username}) снял вам права администратора!')
        logging.info(msg=f'Administrator {callback.from_user.id} removed administrative privileges {callback_data.user_id}')
    else:
        user.is_admin = True
        text = f'✅ Пользователю {callback_data.user_id} (@{user.username}) выданы права администратора!'
        text_user = ('<b>💡 Уведомление</b>\n\n'
                     f'Администратор <b>{callback.from_user.id}</b> (@{callback.from_user.username}) выдал вам права администратора!')
        logging.info(msg=f'Administrator {callback.from_user.id} gave administrative privileges {callback_data.user_id}')
    await session.commit()

    await callback.answer(text=text, show_alert=True)

    user = (await session.execute(select(User).where(User.id == callback_data.user_id))).scalar_one()
    text, keyboard = await user_info(user)
    await callback.message.edit_text(text=text, reply_markup=keyboard)

    try:
        await bot.send_message(chat_id=callback_data.user_id, text=text_user)
    except:
        pass


async def get_users_base(callback: CallbackQuery, session: AsyncSession):
    await callback.message.delete()

    text = '⏳ Подождите, идет формирование базы пользователей!'
    temp_msg = await callback.message.answer(text=text)

    users = (await session.execute(select(User))).scalars()

    data = {}

    for user in users:
        try:
            seniority = user.seniority.strftime('%d.%m.%Y %H:%M')
        except:
            seniority = 'None'
        data[user.id] = {
            'username': user.username,
            'full_name': user.full_name,
            'register_date': user.register_date.strftime('%d.%m.%Y %H:%M'),
            'is_block': user.is_block,
            'is_admin': user.is_admin,
            'phone': user.phone,
            'is_assistant': user.is_assistant,
            'is_doctor': user.is_doctor,
            'is_nurse': user.is_nurse,
            'fio': user.fio,
            'position': user.position,
            'seniority': seniority,
            'calculation': user.calculation
        }

    with open('files/users.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

    file = FSInputFile(path='files/users.json')
    text = '✅ База успешно сформирована!'
    keyboard = inline.return_apanel()

    await temp_msg.delete()
    await callback.message.answer_document(document=file)
    await callback.message.answer(text=text, reply_markup=keyboard)


async def get_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    text = 'Отправьте сообщение для рассылки по пользователям!'
    await callback.message.answer(text=text)
    await state.set_state(APanelState.wait_message)


async def get_message_get_name(message: Message, state: FSMContext):
    await state.clear()
    await state.set_data({'message_id': message.message_id})

    text = 'Желает добавить кнопку со ссылкой в рассылку?'
    keyboard = inline.message_url()
    await message.answer(text=text, reply_markup=keyboard)


async def get_message_url_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    text = 'Отправьте текст для кнопки.'
    await callback.message.answer(text=text)
    await state.set_state(APanelState.wait_message_name)


async def get_message_get_url(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
        return await message.answer(text=text)

    if len(message.text) > 30:
        text = ('❌ <b>Произошла ошибка [2]</b>\n\n'
                '<i>* Длина имени кнопки не должна превышать 30 символов. Повторите ввод!</i>')
        return await message.answer(text=text)

    await state.update_data({'name': message.text})

    text = 'Пришлите ссылку для кнопки.'
    await message.answer(text=text)
    await state.set_state(APanelState.wait_message_url)


async def start_message(message: Message | CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    if isinstance(message, Message):
        if message.content_type != ContentType.TEXT:
            text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                    '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
            return await message.answer(text=text)
        url = True
        await state.update_data({'url': message.text})
        my_id = message.from_user.id
    else:
        await message.message.delete()
        my_id = message.from_user.id
        message = message.message
        url = False

    data = await state.get_data()
    await state.clear()

    users = (await session.execute(select(User))).scalars()
    total = (await session.execute(func.count(User.id))).scalar()

    count, success, error = 0, 0, 0

    text = (f'<b>Статус рассылки</b>\n\n'
            f'┌ Отправлено сообщений: <b>{count}</b> из <b>{total}.</b>\n'
            f'├ Успешно: <b>{success}.</b>\n'
            f'└ С ошибкой: <b>{error}.</b>')

    message_ = await message.answer(text=text)

    for user in users:
        count += 1
        if count % 10 == 0:
            text = (f'<b>Статус рассылки</b>\n\n'
                    f'┌ Отправлено сообщений: <b>{count}</b> из <b>{total}.</b>\n'
                    f'├ Успешно: <b>{success}.</b>\n'
                    f'└ С ошибкой: <b>{error}.</b>')
            await message_.edit_text(text=text)

        try:
            if url:
                keyboard = inline.message_kb(data.get('name'), data.get('url'))
                await bot.copy_message(chat_id=user.id, from_chat_id=my_id, message_id=data.get('message_id'), reply_markup=keyboard)
            else:
                await bot.copy_message(chat_id=user.id, from_chat_id=my_id, message_id=data.get('message_id'))
            success += 1
        except:
            error += 1

    text = (f'<b>Рассылка завершена</b>\n\n'
            f'┌ Отправлено сообщений: <b>{count}.</b>\n'
            f'├ Успешно: <b>{success}.</b>\n'
            f'└ С ошибкой: <b>{error}.</b>')
    keyboard = inline.return_apanel()
    await message_.edit_text(text=text, reply_markup=keyboard)


async def save_role_user(callback: CallbackQuery, session: AsyncSession, callback_data: SetRole, bot: Bot):
    await callback.message.delete()
    user = (await session.execute(select(User).where(User.id == callback_data.user_id))).scalar_one()
    if callback_data.role == 'assistant':
        user.is_assistant = True
        user.is_doctor = False
        user.is_nurse = False
        role = '👩‍⚕️ Ассистент'
    elif callback_data.role == 'doctor':
        user.is_assistant = False
        user.is_doctor = True
        user.is_nurse = False
        role = '👨‍⚕️ Врач'
    elif callback_data.role == 'nurse':
        user.is_assistant = False
        user.is_doctor = False
        user.is_nurse = True
        role = '🧑‍⚕️ Старшая медсестра'
    else:
        user.is_assistant = False
        user.is_doctor = False
        user.is_nurse = False
        role = '❌ Без роли'
    await session.commit()
    text = f'Пользователю <b>{callback_data.user_id}</b> установлена роль <b>{role}</b>'
    keyboard = inline.set_data(callback_data.user_id)
    await callback.message.answer(text=text, reply_markup=keyboard)

    text = f'✅ Вам обновлена роль. Новая роль: <b>{role}</b>'
    try:
        await bot.send_message(chat_id=callback_data.user_id, text=text)
    except:
        pass


async def get_phone_number(message: Message, state: FSMContext, session: AsyncSession):
    if message.content_type != ContentType.TEXT:
        text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
        return await message.answer(text=text)
    data = await state.get_data()
    user = (await session.execute(select(User).where(User.id == data.get('user_id')))).scalar_one()

    text = ('Введите номер телефона.\n'
            f'* Предыдущее значение: {user.phone}')
    await state.update_data({'fio': message.text})
    await state.set_state(APanelState.wait_phone)
    await message.answer(text=text)


async def get_position(message: Message, state: FSMContext, session: AsyncSession):
    if message.content_type != ContentType.TEXT:
        text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
        return await message.answer(text=text)
    data = await state.get_data()
    user = (await session.execute(select(User).where(User.id == data.get('user_id')))).scalar_one()

    text = ('Выберите должность.\n'
            f'* Предыдущее значение: {user.position}')
    await state.update_data({'phone': message.text})
    keyboard = inline.get_position()
    await message.answer(text=text, reply_markup=keyboard)


async def get_start_date(callback: CallbackQuery, session: AsyncSession, callback_data: SetPosition, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    user = (await session.execute(select(User).where(User.id == data.get('user_id')))).scalar_one()

    text = ('Введите дату начала работы в организации. Формат даты: ДД.ММ.ГГГГ\n'
            f'* Предыдущее значение: {user.position}')
    await state.update_data({'position': callback_data.type})
    await state.set_state(APanelState.wait_date_start)
    await callback.message.answer(text=text)


async def get_save_user(message: Message, session: AsyncSession, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        text = ('❌ <b>Произошла ошибка [1]</b>\n\n'
                '<i>* Вы должны отправить текстовое сообщение. Повторите ввод!</i>')
        return await message.answer(text=text)
    data = await state.get_data()
    user = (await session.execute(select(User).where(User.id == data.get('user_id')))).scalar_one()

    try:
        date = datetime.datetime.strptime(message.text, '%d.%m.%Y')
    except:
        text = ('❌ <b>Произошла ошибка [6]</b>\n\n'
                '<i>* Не верный формат даты. Повторите ввод!</i>')
        return await message.answer(text=text)

    user.fio = data.get('fio')
    user.phone = data.get('phone')
    user.position = data.get('position')
    user.seniority = date

    await session.commit()
    text = '✅ Анкета пользователя обновлена.'
    keyboard = inline.return_user_search()
    await message.answer(text=text, reply_markup=keyboard)
    await state.clear()


async def get_report(callback: CallbackQuery, session: AsyncSession):
    async with session:
        month = datetime.datetime.now().month - 1
        year = datetime.datetime.now().year
        if month == 0:
            month = 12
            year -= 1

        jobs = (await session.execute(select(Jobs))).scalars()
        users = (await session.execute(select(User).where(User.is_assistant == True))).scalars()
        data = []
        for user in users:
            jobs_user = (await session.execute(select(Jobs).where(and_((extract('month', Jobs.date) == month), (Jobs.user_id == user.id))))).scalars()
            total_hours = 0
            money = 0
            for job in jobs_user:
                doctor = (await session.execute(select(User).where(User.id == job.doctor_id))).scalar()
                total_hours += job.hours
                price = doctor_price.get(doctor.position)
                if job.second_doctor_rate == 2:
                    price += 50
                elif job.second_doctor_rate == 1:
                    price += 25
                else:
                    pass

                seniority = datetime.datetime.now() - user.seniority
                seniority = seniority.days
                if seniority > 1825:
                    money += 42.5
                elif seniority > 1460:
                    money += 34
                elif seniority > 1095:
                    money += 25.5
                elif seniority > 730:
                    money += 17
                elif seniority > 365:
                    money += 8.5
                else:
                    pass

                if job.nurse_rate == 2:
                    price += 50
                elif job.nurse_rate == 1:
                    price += 25
                else:
                    pass

                money += price * job.hours

                sighting = job.sighting * 50
                optg = job.optg * 100
                kt = job.kt * 150
                trg = job.trg * 100
                blood = job.blood * 150
                implantation = job.implantation * 300

                money += sighting + optg + kt + trg + blood + implantation

            user_stats = {
                'fio': user.fio,
                'phone': user.phone,
                'count_hours': total_hours,
                'money': money
            }
            data.append(user_stats)

        data_jobs = []
        for job in jobs:
            user = (await session.execute(select(User).where(User.id == job.user_id))).scalar()
            doctor = (await session.execute(select(User).where(User.id == job.doctor_id))).scalar()
            if doctor:
                job_user = {
                    'fio': user.fio,
                    'phone': user.phone,
                    'date': job.date.strftime('%d.%m.%Y'),
                    'hours': job.hours,
                    'doctor': doctor.fio,
                    'sighting': job.sighting,
                    'optg': job.optg,
                    'kt': job.kt,
                    'trg': job.trg,
                    'blood': job.blood,
                    'implantation': job.implantation,
                    'doctor_rate': job.doctor_rate,
                    'second_doctor_rate': job.second_doctor_rate,
                    'nurse_rate': job.nurse_rate,
                    'is_nurse': job.is_nurse
                }
                data_jobs.append(job_user)

        with open('assistants.csv', mode='w', encoding='windows-1251') as w_file:
            file_writer = csv.writer(w_file, delimiter=',', lineterminator='\r')
            file_writer.writerow(['ФИО', 'Телефон', 'Отработано часов', 'Расчет'])
            for user in data:
                file_writer.writerow([user.get('fio'), user.get('phone'), user.get('count_hours'), user.get('money')])

        with open('jobs.csv', mode='w', encoding='windows-1251') as w_file:
            file_writer = csv.writer(w_file, delimiter=',', lineterminator='\r')
            file_writer.writerow(['ФИО', 'Телефон', 'Дата', 'Отработал часов', 'Доктор', 'Отработал часов', 'Второй Доктор', 'Прицельный', 'ОПТГ', 'КТ', 'ТРГ', 'Заборов крови', 'Имплантация', 'Оценка врача', 'Оценка второго врача' 'Оценка мед.сестры', 'Проверка мед.сестры'])
            for job in data_jobs:
                file_writer.writerow([job.get('fio'), job.get('phone'), job.get('date'), job.get('hours'), job.get('doctor'), job.get('second_doctor_hours'), job.get('second_doctor'), job.get('sighting'), job.get('optg'), job.get('kt'), job.get('trg'), job.get('blood'), job.get('implantation'), 'Отлично' if job.get('doctor_rate') == 3 else 'Хорошо' if job.get('doctor_rate') == 1 else 'Удовлетворительно', 'Отлично' if job.get('second_doctor_rate') == 3 else 'Хорошо' if job.get('second_doctor_rate') == 1 else 'Удовлетворительно', 'Отлично' if job.get('nurse_rate') == 3 else 'Хорошо' if job.get('nurse_rate') == 1 else 'Удовлетворительно', 'Да' if job.get('is_nurse') == 1 else 'Нет'])

    file_assistants = FSInputFile(path='assistants.csv')
    file_jobs = FSInputFile(path='jobs.csv')

    text = '✅ Ежемесячный отчет сформирован.'

    await callback.message.answer_document(document=file_assistants)
    await callback.message.answer_document(document=file_jobs)
    await callback.message.answer(text=text)

    os.remove('assistants.csv')
    os.remove('jobs.csv')