import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.jobs import Jobs
from database.models.user import User
from keyboards.inline import users as inline
from utils.callbackdata import CheckAssistant, SaveRateAssistant
from utils.state import UserState


async def command_start(message: Message | CallbackQuery, session: AsyncSession, state: FSMContext, is_admin: bool):
    await state.clear()
    user = (await session.execute(select(User).where(User.id == message.from_user.id))).scalar_one_or_none()

    if not user:
        session.add(User(
            id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            register_date=datetime.datetime.now()
        ))
        await session.commit()

    user = (await session.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    if user.is_assistant:
        role = '👩‍⚕️ Ассистент'
    elif user.is_doctor:
        role = '👨‍⚕️ Врач'
    elif user.is_nurse:
        role = '🧑‍⚕️ Старшая медсестра'
    else:
        role = '❌ Без роли'
    text = (f'👋 Привет, <b>{message.from_user.first_name}</b>\n\n'
            f'Ваша роль: <b>{role}</b>\n'
            f'Ваш user_id: <code>{message.from_user.id}</code>\n\n'
            f'Для обновления роли, свяжитесь с администратором, отправив ему свой user_id.')

    if is_admin or user.is_nurse:
        keyboard = inline.main_menu(is_admin, user.is_nurse)

    if isinstance(message, CallbackQuery):
        await message.message.delete()
        message = message.message

    if is_admin or user.is_nurse:
        await message.answer(text=text, reply_markup=keyboard)
    else:
        await message.answer(text=text)


async def get_check_assistant(callback: CallbackQuery, session: AsyncSession):
    await callback.message.delete()

    jobs = (await session.execute(select(Jobs).where(Jobs.is_nurse == False))).scalars()

    text = 'Выберите ассистента для проверки.'
    keyboard = await inline.check_assistant(jobs, session)
    await callback.message.answer(text=text, reply_markup=keyboard)


async def select_check_assistant(callback: CallbackQuery, session: AsyncSession, callback_data: CheckAssistant):
    await callback.message.delete()

    job = (await session.execute(select(Jobs).where(Jobs.id == callback_data.job_id))).scalar()
    user = (await session.execute(select(User).where(User.id == job.user_id))).scalar()
    doctor = (await session.execute(select(User).where(User.id == job.doctor_id))).scalar()

    text = (f'👩‍⚕️ Ассистент: <b>{user.fio}</b>\n'
            f'🕓 Дата работы: <b>{job.date.strftime("%d.%m.%Y")}</b>\n'
            f'👨‍⚕️ Врач: <b>{doctor.fio}</b>\n\n'
            f'⏳ Отработано часов: <b>{job.hours} ч.</b>\n\n'
            f'╔ Прицельных процедур: <b>{job.sighting}</b>\n'
            f'╠ ОПТГ: <b>{job.optg}</b>\n'
            f'╠ КТ: <b>{job.kt}</b>\n'
            f'╠ ТРГ: <b>{job.trg}</b>\n'
            f'╠ Заборов крови: <b>{job.blood}</b>\n'
            f'╚ Имплантаций: <b>{job.implantation}</b>\n\n'
            f'🌟 Оценка доктора: <b>{"Удовлетворительно" if job.doctor_rate == 0 else "Хорошо" if job.doctor_rate == 1 else "Отлично"}</b>\n'
            f'🌟 Оценка мед.сестры: <b>{"Удовлетворительно" if job.nurse_rate == 0 else "Хорошо" if job.nurse_rate == 1 else "Отлично"}</b>\n\n'
            f'Проверьте данные. Если данные не верны измените их и поставьте оценку.')
    keyboard = inline.get_save_job(callback_data.job_id)
    await callback.message.answer(text=text, reply_markup=keyboard)


async def action_assistant(callback: CallbackQuery, callback_data: SaveRateAssistant, session: AsyncSession, state: FSMContext):
    if callback_data.action.startswith('edit'):
        await callback.message.delete()
        type_edit = callback_data.action.split('_')[1]
        await state.set_data({'job_id': callback_data.job_id, 'type': type_edit})
        text = 'Введите новое значение.'
        await callback.message.answer(text=text)
        await state.set_state(UserState.wait_procedur)
    else:
        rate = int(callback_data.action.split('_')[1])
        job = (await session.execute(select(Jobs).where(Jobs.id == callback_data.job_id))).scalar()
        job.nurse_rate = rate
        await session.commit()

        job = (await session.execute(select(Jobs).where(Jobs.id == callback_data.job_id))).scalar()
        user = (await session.execute(select(User).where(User.id == job.user_id))).scalar()
        doctor = (await session.execute(select(User).where(User.id == job.doctor_id))).scalar()

        text = (f'👩‍⚕️ Ассистент: <b>{user.fio}</b>\n'
                f'🕓 Дата работы: <b>{job.date.strftime("%d.%m.%Y")}</b>\n'
                f'👨‍⚕️ Врач: <b>{doctor.fio}</b>\n\n'
                f'⏳ Отработано часов: <b>{job.hours} ч.</b>\n\n'
                f'╔ Прицельных процедур: <b>{job.sighting}</b>\n'
                f'╠ ОПТГ: <b>{job.optg}</b>\n'
                f'╠ КТ: <b>{job.kt}</b>\n'
                f'╠ ТРГ: <b>{job.trg}</b>\n'
                f'╠ Заборов крови: <b>{job.blood}</b>\n'
                f'╚ Имплантаций: <b>{job.implantation}</b>\n\n'
                f'🌟 Оценка доктора: <b>{"Удовлетворительно" if job.doctor_rate == 0 else "Хорошо" if job.doctor_rate == 1 else "Отлично"}</b>\n'
                f'🌟 Оценка мед.сестры: <b>{"Удовлетворительно" if job.nurse_rate == 0 else "Хорошо" if job.nurse_rate == 1 else "Отлично"}</b>\n\n'
                f'Проверьте данные. Если данные не верны измените их и поставьте оценку.')
        keyboard = inline.get_save_job(callback_data.job_id)
        try:
            await callback.message.edit_text(text=text, reply_markup=keyboard)
        except:
            pass
        text = '✅ Оценка сохранена.'
        await callback.answer(text=text, show_alert=True)


async def update_procedur(message: Message, state: FSMContext, session: AsyncSession):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)
    data = await state.get_data()
    job = (await session.execute(select(Jobs).where(Jobs.id == data.get('job_id')))).scalar()
    if data.get('type') == 'sighting':
        job.sighting = count
    elif data.get('type') == 'optg':
        job.optg = count
    elif data.get('type') == 'kt':
        job.kt = count
    elif data.get('type') == 'trg':
        job.trg = count
    elif data.get('type') == 'blood':
        job.blood = count
    elif data.get('type') == 'time':
        job.time = count
    else:
        job.implantation = count
    await session.commit()

    job = (await session.execute(select(Jobs).where(Jobs.id == data.get('job_id')))).scalar()
    user = (await session.execute(select(User).where(User.id == job.user_id))).scalar()
    doctor = (await session.execute(select(User).where(User.id == job.doctor_id))).scalar()

    text = (f'👩‍⚕️ Ассистент: <b>{user.fio}</b>\n'
            f'🕓 Дата работы: <b>{job.date.strftime("%d.%m.%Y")}</b>\n'
            f'👨‍⚕️ Врач: <b>{doctor.fio}</b>\n\n'
            f'⏳ Отработано часов: <b>{job.hours} ч.</b>\n\n'
            f'╔ Прицельных процедур: <b>{job.sighting}</b>\n'
            f'╠ ОПТГ: <b>{job.optg}</b>\n'
            f'╠ КТ: <b>{job.kt}</b>\n'
            f'╠ ТРГ: <b>{job.trg}</b>\n'
            f'╠ Заборов крови: <b>{job.blood}</b>\n'
            f'╚ Имплантаций: <b>{job.implantation}</b>\n\n'
            f'🌟 Оценка доктора: <b>{"Удовлетворительно" if job.doctor_rate == 0 else "Хорошо" if job.doctor_rate == 1 else "Отлично"}</b>\n'
            f'🌟 Оценка мед.сестры: <b>{"Удовлетворительно" if job.nurse_rate == 0 else "Хорошо" if job.nurse_rate == 1 else "Отлично"}</b>\n\n'
            f'Проверьте данные. Если данные не верны измените их и поставьте оценку.')
    keyboard = inline.get_save_job(data.get('job_id'))
    await message.answer(text=text, reply_markup=keyboard)


async def test_callback(callback: CallbackQuery):
    text = '❌ Функционала еще нет'
    await callback.answer(text=text, show_alert=True)
