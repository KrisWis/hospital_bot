from aiogram.filters.callback_data import CallbackData


class UserInfoData(CallbackData, prefix='UserInfoData'):
    user_id: int
    action: str


class SetRole(CallbackData, prefix='SetRole'):
    user_id: int
    role: str


class SetPosition(CallbackData, prefix='SetPosition'):
    type: str


class HoursJobs(CallbackData, prefix='HoursJobs'):
    hours: int

class SecondDoctorHoursJobs(CallbackData, prefix='SecondDoctorHoursJobs'):
    hours: int

class DoctorsData(CallbackData, prefix='DoctorsData'):
    id: int

class SecondDoctorsData(CallbackData, prefix='SecondDoctorsData'):
    id: int

class DoctorRate(CallbackData, prefix='DoctorRate'):
    rate: int
    job_id: int

class SecondDoctorRate(CallbackData, prefix='SecondDoctorRate'):
    rate: int
    job_id: int

class CheckAssistant(CallbackData, prefix='CheckAssistant'):
    job_id: int


class SaveRateAssistant(CheckAssistant, prefix='SaveRateAssistant'):
    job_id: int
    action: str
