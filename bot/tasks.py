from datetime import datetime, timedelta
from typing import List

import pytz
from apscheduler.job import Job
from apscheduler.triggers.date import DateTrigger
from loguru import logger
from tortoise.expressions import Q

from bot.misc import bot, scheduler
from bot.models import User


async def notify(user: int, text: str):
    logger.debug(f"Task triggered: {user} - {text}")
    await bot.send_message(chat_id=user, text=text)


async def notify_all(text: str):
    logger.debug(f"Task triggered: {text}")
    users = await User.all()
    for user in users:
        await bot.send_message(chat_id=user.user_id, text=text)


async def notify_birthday(
    birtday_user: int, days_left: int, preference: str, date: str
):
    logger.debug(f"Task triggered: {birtday_user}")
    # users is a list of User objects except the one who has birthday
    users = await User.all().filter(~Q(user_id=birtday_user))
    phonetic = await User.get(user_id=birtday_user)
    if not phonetic:
        logger.error(f"User {birtday_user} not found")
        return
    if days_left > 4:
        message = f"День рождения у <b>{phonetic.full_name}</b>{' ( @'+str(phonetic.username)+' )' if phonetic.username else ''} через <b>{days_left}</b> дней!\n\nЕго/её предпочтения:\n{preference}\n\nТочная дата: <b>{date}</b>\n\nНа подарок - 200 Руб. <code>2200700602143611</code> Анна."
    elif days_left > 1:
        message = f"День рождения у <b>{phonetic.full_name}</b>{' ( @'+str(phonetic.username)+' )' if phonetic.username else ''} через <b>{days_left}</b> дня!\n\nЕго/её предпочтения:\n<b>{preference}</b>\n\nТочная дата: <b>{date}</b>\n\nНа подарок - 200 Руб. <code>2200700602143611</code> Анна."
    elif days_left == 1:
        message = f"День рождения у <b>{phonetic.full_name}</b>{' ( @'+str(phonetic.username)+' )' if phonetic.username else ''} <b>завтра</b>!\n\nЕго/её предпочтения:\n<b>{preference}</b>\n\nТочная дата: <b>{date}</b>\n\nНа подарок - 200 Руб. <code>2200700602143611</code> Анна."
    else:
        message = f"День рождения у <b>{phonetic.full_name}</b>{' ( @'+str(phonetic.username)+' )' if phonetic.username else ''} <b>сегодня</b>!\n\nЕго/её предпочтения:\n<b>{preference}</b>\n\nТочная дата: <b>{date}</b>\n\nНа подарок - 200 Руб. <code>2200700602143611</code> Анна."

    for user in users:
        logger.debug(f"Sending message to {user.user_id}")
        await bot.send_message(chat_id=user.user_id, text=message)


async def schedule_birthday(phonetic: User, birthday: datetime, preference: str):
    logger.debug(f"Scheduling birthday for {phonetic.user_id}")
    existing_jobs = await get_jobs(phonetic)
    for job in existing_jobs:
        logger.debug(f"Removing job {job.id}")
        scheduler.remove_job(job.id)
    today = datetime.now(tz=pytz.timezone("Europe/Moscow"))
    if birthday.month == today.month and birthday.day == today.day:
        await notify_birthday(
            phonetic.user_id, 0, preference, birthday.strftime("%d.%m.%Y")
        )
        return
    if birthday.month < today.month or (
        birthday.month == today.month and birthday.day < today.day
    ):
        birthday = birthday.replace(year=today.year + 1)

    # # DEBUG ONLY
    # birthday = datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(seconds=60)
    # # DEBUG ONLY

    days_left = (birthday - today).days
    logger.debug(f"Days left: {days_left}")
    birthday_str = birthday.strftime("%d.%m.%Y")
    # Schedule 3 notifications: 3 days before, 1 day before and on the day

    trigger = DateTrigger(
        birthday - timedelta(days=3), timezone=pytz.timezone("Europe/Moscow")
    )

    # # DEBUG ONLY
    # trigger = DateTrigger(
    #     datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(seconds=30),
    #     timezone=pytz.timezone("Europe/Moscow"),
    # )
    # # DEBUG ONLY
    scheduler.add_job(
        notify_birthday,
        trigger,
        args=[phonetic.user_id, 3, preference, birthday_str],
        id=f"birthday-{phonetic.user_id}-3-{birthday.year}",
        name=f"Уведомление о дне рождения {phonetic.full_name} за 3 дня",
    )

    trigger = DateTrigger(
        birthday - timedelta(days=1), timezone=pytz.timezone("Europe/Moscow")
    )
    # # DEBUG ONLY
    # trigger = DateTrigger(
    #     datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(seconds=50),
    #     timezone=pytz.timezone("Europe/Moscow"),
    # )
    # # DEBUG ONLY

    scheduler.add_job(
        notify_birthday,
        trigger,
        args=[phonetic.user_id, 1, preference, birthday_str],
        id=f"birthday-{phonetic.user_id}-1-{birthday.year}",
        name=f"Уведомление о дне рождения {phonetic.full_name} за 1 день",
    )

    trigger = DateTrigger(birthday, timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(
        notify_birthday,
        trigger,
        args=[phonetic.user_id, 0, preference, birthday_str],
        id=f"birthday-{phonetic.user_id}-0-{birthday.year}",
        name=f"Уведомление о дне рождения {phonetic.full_name} в день рождения",
    )

    logger.debug(f"Job scheduled for {phonetic.user_id}")


async def get_jobs(user: User) -> List[Job]:
    jobs = scheduler.get_jobs()
    user_jobs = []
    for job in jobs:
        if job.id.startswith(f"birthday-{user.user_id}"):
            user_jobs.append(job)
    return user_jobs
