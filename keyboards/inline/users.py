from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from utils.callbackdata import HoursJobs, DoctorsData, DoctorRate, CheckAssistant, SaveRateAssistant, SecondDoctorsData, SecondDoctorHoursJobs, SecondDoctorRate


def main_menu(is_admin, is_nurse):
    builder = InlineKeyboardBuilder()

    if is_admin:
        builder.button(text='⚙️ Панель управления', callback_data='GetAPanel')

    if is_nurse:
        builder.button(text='Получить отчёт', callback_data='GetAReport')

    return builder.adjust(1).as_markup()


def hours_jobs():
    builder = InlineKeyboardBuilder()

    builder.button(text='1', callback_data=HoursJobs(hours=1))
    builder.button(text='2', callback_data=HoursJobs(hours=2))
    builder.button(text='3', callback_data=HoursJobs(hours=3))
    builder.button(text='4', callback_data=HoursJobs(hours=4))
    builder.button(text='5', callback_data=HoursJobs(hours=5))
    builder.button(text='6', callback_data=HoursJobs(hours=6))
    builder.button(text='7', callback_data=HoursJobs(hours=7))
    builder.button(text='8', callback_data=HoursJobs(hours=8))
    builder.button(text='9', callback_data=HoursJobs(hours=9))
    builder.button(text='10', callback_data=HoursJobs(hours=10))
    builder.button(text='11', callback_data=HoursJobs(hours=11))
    builder.button(text='12', callback_data=HoursJobs(hours=12))
    builder.button(text='Выходной', callback_data=HoursJobs(hours=0))

    return builder.adjust(6, 6, 1).as_markup()


def second_doctor_hours_jobs():
    builder = InlineKeyboardBuilder()

    builder.button(text='1', callback_data=SecondDoctorHoursJobs(hours=1))
    builder.button(text='2', callback_data=SecondDoctorHoursJobs(hours=2))
    builder.button(text='3', callback_data=SecondDoctorHoursJobs(hours=3))
    builder.button(text='4', callback_data=SecondDoctorHoursJobs(hours=4))
    builder.button(text='5', callback_data=SecondDoctorHoursJobs(hours=5))
    builder.button(text='6', callback_data=SecondDoctorHoursJobs(hours=6))
    builder.button(text='7', callback_data=SecondDoctorHoursJobs(hours=7))
    builder.button(text='8', callback_data=SecondDoctorHoursJobs(hours=8))
    builder.button(text='9', callback_data=SecondDoctorHoursJobs(hours=9))
    builder.button(text='10', callback_data=SecondDoctorHoursJobs(hours=10))
    builder.button(text='11', callback_data=SecondDoctorHoursJobs(hours=11))
    builder.button(text='12', callback_data=SecondDoctorHoursJobs(hours=12))

    return builder.adjust(6, 6, 1).as_markup()


def select_doctor(doctors):
    builder = InlineKeyboardBuilder()

    for doctor in doctors:
        builder.button(text=f'{doctor.fio}', callback_data=DoctorsData(id=doctor.id))

    return builder.adjust(1).as_markup()


def select_second_doctor(doctors):
    builder = InlineKeyboardBuilder()

    for doctor in doctors:
        builder.button(text=f'{doctor.fio}', callback_data=SecondDoctorsData(id=doctor.id))

    builder.button(text='Пропустить', callback_data=SecondDoctorsData(id=-1))
    return builder.adjust(1).as_markup()


def rate_doctor(job_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='Удовлетворительно', callback_data=DoctorRate(rate=0, job_id=job_id))
    builder.button(text='Хорошо', callback_data=DoctorRate(rate=1, job_id=job_id))
    builder.button(text='Отлично', callback_data=DoctorRate(rate=2, job_id=job_id))

    return builder.adjust(1).as_markup()


def rate_second_doctor(job_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='Удовлетворительно', callback_data=SecondDoctorRate(rate=0, job_id=job_id))
    builder.button(text='Хорошо', callback_data=SecondDoctorRate(rate=1, job_id=job_id))
    builder.button(text='Отлично', callback_data=SecondDoctorRate(rate=2, job_id=job_id))

    return builder.adjust(1).as_markup()


async def check_assistant(jobs, session: AsyncSession):
    builder = InlineKeyboardBuilder()

    for job in jobs:
        user = (await session.execute(select(User).where(User.id == job.user_id))).scalar()
        if user.fio:
            builder.button(text=f'{user.fio}', callback_data=CheckAssistant(job_id=job.id))

    builder.button(text='Завершить оценивание', callback_data='EndChecking')
    builder.button(text='📌 Главное меню', callback_data='GetStart')

    return builder.adjust(1).as_markup()


def get_save_job(job_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='➖ Изменить часы', callback_data=SaveRateAssistant(job_id=job_id, action='edit_time'))
    builder.button(text='➖ Изменить прицельные', callback_data=SaveRateAssistant(job_id=job_id, action='edit_sighting'))
    builder.button(text='➖ Изменить ОПТГ', callback_data=SaveRateAssistant(job_id=job_id, action='edit_optg'))
    builder.button(text='➖ Изменить КТ', callback_data=SaveRateAssistant(job_id=job_id, action='edit_kt'))
    builder.button(text='➖ Изменить ТРГ', callback_data=SaveRateAssistant(job_id=job_id, action='edit_trg'))
    builder.button(text='➖ Изменить забор крови', callback_data=SaveRateAssistant(job_id=job_id, action='edit_blood'))
    builder.button(text='➖ Изменить имплантацию', callback_data=SaveRateAssistant(job_id=job_id, action='edit_implantation'))
    builder.button(text='Удовлетворительно', callback_data=SaveRateAssistant(job_id=job_id, action='save_0'))
    builder.button(text='Хорошо', callback_data=SaveRateAssistant(job_id=job_id, action='save_1'))
    builder.button(text='Отлично', callback_data=SaveRateAssistant(job_id=job_id, action='save_3'))
    builder.button(text='🔙 Назад', callback_data='GetCheckAssistant')

    return builder.adjust(2, 2, 2, 1, 2, 1).as_markup()


def return_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text='🔙 Назад', callback_data='GetCheckAssistant')

    return builder.adjust(1).as_markup()
