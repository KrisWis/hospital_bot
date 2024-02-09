import csv
import datetime
import os

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

from sqlalchemy import select, extract, and_
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import CREATOR
from database.models.jobs import Jobs
from database.models.user import User
from keyboards.inline import users as inline
from utils.callbackdata import HoursJobs, DoctorsData, DoctorRate, SecondDoctorsData, SecondDoctorRate
from utils.state import UserState
from database.engine import create_session_maker
from aiogram.enums import ParseMode
from config import TOKEN
from aiogram.utils.keyboard import InlineKeyboardBuilder


doctor_price = {
    'Терапия': 300,
    'Ортопедия': 300,
    'Ортодонтия': 300,
    'Хирургия': 330,
}


async def choose_doctor(bot: Bot, sessionmaker: async_sessionmaker):
    async with sessionmaker() as session:

        doctors = (await session.execute(select(User).where(User.is_doctor))).scalars()
        keyboard = inline.select_doctor(doctors)

        users = (await session.execute(select(User).where(User.is_assistant == True))).scalars()
        for user in users:
            text = f'👋 Привет, <b>{user.full_name}</b>\n\nРабочий день завершен. C каким врачом вы сегодня работали?'
            try:
                await bot.send_message(chat_id=user.id, text=text, reply_markup=keyboard)
            except:
                pass


async def select_doctor_hours(callback: CallbackQuery, callback_data: HoursJobs, state: FSMContext):
    await callback.message.delete()
    await state.update_data({'doctor': callback_data.id})

    text = 'Cколько часов вы c ним сегодня отработали?'
    keyboard = inline.hours_jobs()
    await callback.message.answer(text=text, reply_markup=keyboard)


async def choose_second_doctor(callback: CallbackQuery, state: FSMContext, callback_data: DoctorsData, session: AsyncSession):
    await callback.message.delete()
    await state.set_data({'doctor_hours': callback_data.hours})

    if callback_data.hours == 0:
        text = 'Спасибо за ответ.'
        return await callback.message.answer(text=text)

    elif callback_data.hours == 12:
        text = ('Сколько процедур <b>"прицельный"</b> вы сегодня сделали?\n\n'
                '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
        await state.set_state(UserState.wait_sighting)
        return await callback.message.answer(text=text)

    doctors = (await session.execute(select(User).where(User.is_doctor))).scalars()

    text = 'Выберите с каким ещё врачом сегодня работали.'
    keyboard = inline.select_second_doctor(doctors)
    await callback.message.answer(text=text, reply_markup=keyboard)


async def select_second_doctor_hours(callback: CallbackQuery, callback_data: HoursJobs, state: FSMContext):
    await callback.message.delete()

    if callback_data.id == -1:
        text = ('Сколько процедур <b>"прицельный"</b> вы сегодня сделали?\n\n'
                '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
        await state.set_state(UserState.wait_sighting)
        return await callback.message.answer(text=text)
    
    await state.update_data({'second_doctor': callback_data.id})
    text = 'Сколько часов вы c ним сегодня отработали?'
    keyboard = inline.second_doctor_hours_jobs()
    await callback.message.answer(text=text, reply_markup=keyboard)


async def get_count_jobs_one(callback: CallbackQuery, state: FSMContext, callback_data: SecondDoctorsData):
    await callback.message.delete()
    if callback_data.hours:
        await state.set_data({'second_doctor_hours': callback_data.hours})

    text = ('Сколько процедур <b>"прицельный"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await callback.message.answer(text=text)
    await state.set_state(UserState.wait_sighting)


async def get_count_jobs_two(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'sighting': count})

    text = ('Сколько процедур <b>"ОПТГ"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await message.answer(text=text)
    await state.set_state(UserState.wait_optg)


async def get_count_jobs_three(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'optg': count})

    text = ('Сколько процедур <b>"КТ"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await message.answer(text=text)
    await state.set_state(UserState.wait_kt)


async def get_count_jobs_four(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'kt': count})

    text = ('Сколько процедур <b>"ТРГ"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await message.answer(text=text)
    await state.set_state(UserState.wait_trg)


async def get_count_jobs_five(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'trg': count})

    text = ('Сколько процедур <b>"Забор крови"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await message.answer(text=text)
    await state.set_state(UserState.wait_blood)


async def get_count_jobs_six(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'blood': count})

    text = ('Сколько процедур <b>"Имплантация"</b> вы сегодня сделали?\n\n'
            '* Пришлите ответ числом, если не выполняли данные процедуры, отправьте 0')
    await message.answer(text=text)
    await state.set_state(UserState.wait_implantation)


async def get_count_jobs_save(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    try:
        count = int(message.text)
    except:
        text = '❌ Вы должны прислать число. Повторите ввод.'
        return await message.answer(text=text)

    if count < 0:
        text = '❌ Значение процедур не должно быть меньше 0. Повторите ввод.'
        return await message.answer(text=text)

    await state.update_data({'implantation': count})

    data = await state.get_data()
    jobs_all = (await session.execute(select(Jobs).where(and_(Jobs.user_id == message.from_user.id, Jobs.is_nurse == False))))

    try:
        for job in jobs_all:
            job.is_nurse = True
    except: 
        pass

    await session.commit()
    job = Jobs(
        user_id = message.from_user.id,
        doctor_id = data.get('doctor'),
        second_doctor_id = data.get('second_doctor'),
        date = datetime.datetime.now(),
        hours = data.get('doctor_hours'),
        second_doctor_hours = data.get('second_doctor_hours'),
        sighting = data.get('sighting'),
        optg=data.get('optg'),
        kt=data.get('kt'),
        trg=data.get('trg'),
        blood=data.get('blood'),
        implantation=data.get('implantation')
    )

    session.add(job)
    await session.commit()
    text = '✅ Данные сохранены.'
    await message.answer(text=text)
    await state.clear()
    user = (await session.execute(select(User).where(User.id == message.from_user.id))).scalar()
    text = (f'Сегодня вы работали с ассистентом {user.fio}.\n'
            f'Поставьте оценку.')
    keyboard = inline.rate_doctor(job.id)
    try:
        await bot.send_message(chat_id=job.doctor_id, text=text, reply_markup=keyboard)
        keyboard = inline.rate_second_doctor(job.id)
        await bot.send_message(chat_id=job.second_doctor_id, text=text, reply_markup=keyboard)
    except:
        pass


async def save_rate(callback: CallbackQuery, callback_data: DoctorRate, session: AsyncSession):
    await callback.message.delete()

    job = (await session.execute(select(Jobs).where(Jobs.id == callback_data.job_id))).scalar()
    job.doctor_rate = callback_data.rate
    await session.commit()

    text = '✅ Оценка сохранена.'
    await callback.message.answer(text=text)


async def second_doctor_save_rate(callback: CallbackQuery, callback_data: SecondDoctorRate, session: AsyncSession):
    await callback.message.delete()

    job = (await session.execute(select(Jobs).where(Jobs.id == callback_data.job_id))).scalar()
    job.second_doctor_rate = callback_data.rate
    await session.commit()

    text = '✅ Оценка сохранена.'
    await callback.message.answer(text=text)


async def create_report(bot: Bot, sessionmaker: async_sessionmaker):
    async with sessionmaker() as session:
        month = datetime.datetime.now().month - 1
        year = datetime.datetime.now().year
        if month == 0:
            month = 12
            year -= 1

        #jobs = (await session.execute(select(Jobs).where(extract('month', Jobs.date) == month))).scalars()
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
                if job.doctor_rate == 2:
                    price += 50
                elif job.doctor_rate == 1:
                    price += 25
                else:
                    pass

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

        try:
            await bot.send_document(chat_id=CREATOR, document=file_assistants)
            await bot.send_document(chat_id=CREATOR, document=file_jobs)
            await bot.send_message(chat_id=CREATOR, text=text)
        except:
            pass

        users = (await session.execute(select(User).where(User.is_admin == True))).scalars()
        for user in users:
            try:
                await bot.send_document(chat_id=user.id, document=file_assistants)
                await bot.send_document(chat_id=user.id, document=file_jobs)
                await bot.send_message(chat_id=user.id, text=text)
            except:
                pass

    os.remove('assistants.csv')
    os.remove('jobs.csv')


async def rate_assistants(bot: Bot, sessionmaker: async_sessionmaker):
    builder = InlineKeyboardBuilder()
    builder.button(text='Проверить ассистентов', callback_data='GetCheckAssistant')
    keyboard = builder.adjust(1).as_markup()

    async with sessionmaker() as session:

        nurses = (await session.execute(select(User).where(User.is_nurse))).scalars()

        for nurse in nurses:
            text = f'Оцените ассистентов!'
            try:
                await bot.send_message(chat_id=nurse.id, text=text, reply_markup=keyboard)
            except:
                pass