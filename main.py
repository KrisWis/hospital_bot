from logging import basicConfig, INFO
from asyncio import run

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN
from database.engine import create_session_maker
from filters.admin import UserAdminFilter
from filters.banned import UserBannedFilter
from handlers import users, apanel, apsched
from middlewares.session import SessionMiddleware
from utils.callbackdata import UserInfoData, SecondDoctorRate, SetRole, SetPosition, HoursJobs, DoctorsData, DoctorRate, CheckAssistant, SaveRateAssistant, SecondDoctorsData, SecondDoctorHoursJobs
from utils.commands import set_commands
from utils.state import APanelState, UserState


async def main():
    basicConfig(level=INFO, format='[%(asctime)s][%(levelname)s]: file = %(filename)s | message =  %(message)s')

    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    sessionmaker = await create_session_maker()
    dp.update.outer_middleware.register(SessionMiddleware(sessionmaker))

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(apsched.choose_doctor, trigger='cron', hour=20, minute=0, kwargs={'bot': bot, 'sessionmaker': sessionmaker})

    scheduler.add_job(apsched.rate_assistants, trigger='cron', day=1, hour=0, kwargs={'bot': bot, 'sessionmaker': sessionmaker})
    #scheduler.add_job(apsched.rate_assistants, trigger='cron', hour=12, minute=55, kwargs={'bot': bot, 'sessionmaker': sessionmaker})

    scheduler.start()

    await set_commands(bot)

    dp.message.register(users.command_start, CommandStart(), UserBannedFilter())
    dp.callback_query.register(users. command_start, F.data == 'GetStart', UserBannedFilter())
    dp.callback_query.register(users.test_callback, F.data == 'Test', UserBannedFilter())

    dp.callback_query.register(apsched.select_doctor_hours, DoctorsData.filter(), UserBannedFilter())

    dp.callback_query.register(apsched.choose_second_doctor, HoursJobs.filter(), UserBannedFilter())

    dp.callback_query.register(apsched.select_second_doctor_hours, SecondDoctorsData.filter(), UserBannedFilter())

    dp.callback_query.register(apsched.get_count_jobs_one, SecondDoctorHoursJobs.filter(), UserBannedFilter())
    
    dp.message.register(apsched.get_count_jobs_two, UserState.wait_sighting, UserBannedFilter())
    dp.message.register(apsched.get_count_jobs_three, UserState.wait_optg, UserBannedFilter())
    dp.message.register(apsched.get_count_jobs_four, UserState.wait_kt, UserBannedFilter())
    dp.message.register(apsched.get_count_jobs_five, UserState.wait_trg, UserBannedFilter())
    dp.message.register(apsched.get_count_jobs_six, UserState.wait_blood, UserBannedFilter())
    dp.message.register(apsched.get_count_jobs_save, UserState.wait_implantation, UserBannedFilter())
    dp.callback_query.register(apsched.save_rate, DoctorRate.filter(), UserBannedFilter())


    dp.callback_query.register(apsched.second_doctor_save_rate, SecondDoctorRate.filter(), UserBannedFilter())


    dp.callback_query.register(users.get_check_assistant, F.data == 'GetCheckAssistant', UserBannedFilter())
    dp.callback_query.register(users.select_check_assistant, CheckAssistant.filter(), UserBannedFilter())
    dp.callback_query.register(users.action_assistant, SaveRateAssistant.filter(), UserBannedFilter())
    dp.message.register(users.update_procedur, UserState.wait_procedur, UserBannedFilter())

    # Панель управления
    dp.callback_query.register(apanel.get_apanel, F.data == 'GetAPanel', UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.apanel_refresh, F.data == 'APanelRefresh', UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.get_users, F.data == 'GetUsers', UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.select_user, APanelState.wait_user, UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.edit_user, UserInfoData.filter(), UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.get_users_base, F.data == 'GetUsersBase', UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.get_message, F.data == 'GetMessage', UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.get_message_get_name, APanelState.wait_message, UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.get_message_url_name, F.data == 'GetMessageUrlYes', UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.get_message_get_url, APanelState.wait_message_name, UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.start_message, APanelState.wait_message_url, UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.start_message, F.data == 'GetMessageUrlNo', UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.save_role_user, SetRole.filter(), UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.get_phone_number, APanelState.wait_fio, UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.get_position, APanelState.wait_phone, UserBannedFilter(), UserAdminFilter())
    dp.callback_query.register(apanel.get_start_date, SetPosition.filter(), UserBannedFilter(), UserAdminFilter())
    dp.message.register(apanel.get_save_user, APanelState.wait_date_start, UserBannedFilter(), UserAdminFilter())

    dp.callback_query.register(apanel.get_report, F.data == 'GetAReport', UserBannedFilter(), UserAdminFilter())

    dp.callback_query.register(apanel.get_report, F.data == 'EndChecking', UserBannedFilter(), UserAdminFilter())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
