import datetime
from typing import List

import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.job import Job
from loguru import logger

from bot import tasks
from bot.controllers import user as u
from bot.markups.inline_markups import back, confirmation, day_select, month_select
from bot.misc import bot, scheduler


async def jobs(message: types.Message, state: FSMContext):
    reply = await message.answer("⏳ Загружаю список предстоящих уведомлений...")
    user = await u.get_user(message.from_user.id)
    if not user:
        await reply.edit_text(
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться."
        )
        return
    jobs: List[Job] = scheduler.get_jobs()
    jobs_list = "\n".join(
        [
            f"🕒 {job.trigger.run_date.strftime('%d/%m/%Y, %H:%M:%S')} - {job.name}"
            for job in jobs
        ][: min(len(jobs), 10)]
    )

    if not jobs_list:
        jobs_list = "\nПусто 😕\n"
    await reply.edit_text(
        f"Вот все предстоящие уведомления (первые 10): \n\n{jobs_list}"
    )


class Form(StatesGroup):
    month = State()
    day = State()
    preference = State()
    confirm = State()


async def create_month(message: types.Message, state: FSMContext):
    user = await u.get_user(message.from_user.id)
    if not user:
        await message.answer(
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться."
        )
        return
    await Form.month.set()
    await message.answer("1/3 - Выбери месяц: ", reply_markup=month_select())


async def create_day(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    if callback_query.data == "cancel":
        await state.finish()
        return

    user = await u.get_user(callback_query.from_user.id)
    if not user:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться.",
        )
        return
    month = int(callback_query.data)
    await state.update_data(month=month)
    await Form.next()
    await bot.send_message(
        user.user_id, text="2/3 - Выбери день: ", reply_markup=day_select(month)
    )


async def create_preference(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "ignore":
        return

    await callback_query.message.delete()

    if callback_query.data == "back":
        await Form.month.set()
        await bot.send_message(
            callback_query.from_user.id,
            "1/2 - Выбери месяц: ",
            reply_markup=month_select(),
        )
        return

    user = await u.get_user(callback_query.from_user.id)
    if not user:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться.",
        )
        return

    day = int(callback_query.data)
    await state.update_data(day=day)
    await Form.next()
    await bot.send_message(
        user.user_id,
        "3/3 - Выбери, что ты хочешь на день рождения (пожелание к подарку): ",
        reply_markup=back(),
    )


async def create_preference_back(
    callback_query: types.CallbackQuery, state: FSMContext
):
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    if callback_query.data == "ignore":
        return
    if callback_query.data == "back":
        await Form.day.set()
        data = await state.get_data()
        await bot.send_message(
            callback_query.from_user.id,
            text="2/3 - Выбери день: ",
            reply_markup=day_select(data["month"]),
        )
        return


async def create(message: types.Message, state: FSMContext):
    try:
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        logger.error(f"Error while deleting message: {message.message_id - 1}")
    user = await u.get_user(message.from_user.id)
    if not user:
        await bot.send_message(
            message.from_user.id,
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться.",
        )
        return
    preference = message.text
    await state.update_data(preference=preference)
    data = await state.get_data()
    await Form.confirm.set()
    today = datetime.datetime.today()
    date = datetime.datetime(year=today.year, month=data["month"], day=data["day"])
    await bot.send_message(
        user.user_id,
        text=f"🎉 <b>Подтверждение</b>\n\nТвой день рождения: <b>{date.strftime('%d %B')}</b>\nТвое пожелание: <b>{data['preference']}</b>",
        reply_markup=confirmation(),
    )


async def create_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    if callback_query.data == "ignore":
        return
    if callback_query.data == "back":
        await Form.preference.set()
        await bot.send_message(
            callback_query.from_user.id,
            text="3/3 - Выбери, что ты хочешь на день рождения (пожелание к подарку): ",
            reply_markup=back(),
        )
        return
    if callback_query.data == "cancel":
        await state.finish()
        await bot.send_message(
            callback_query.from_user.id,
            text="❌ Отменено!",
        )
        return
    user = await u.get_user(callback_query.from_user.id)
    if not user:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться.",
        )
        return

    data = await state.get_data()
    today = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
    date = datetime.datetime(
        year=today.year,
        month=data["month"],
        day=data["day"],
        hour=7,
        minute=0,
        second=0,
        tzinfo=pytz.timezone("Europe/Moscow"),
    )
    try:
        await tasks.schedule_birthday(user, date, data["preference"])
    except Exception as e:
        logger.error(f"Error while scheduling birthday: {e}")
        await bot.send_message(
            callback_query.from_user.id,
            text=f"❌ Произошла ошибка при планировании уведомления! Вот информация об ошибке:\n\n{e}",
        )
    await bot.send_message(
        callback_query.from_user.id,
        text="✅ Готово! Если ты добавлял уведомление ранее, то оно было удалено и заменено на новое.",
    )
    await state.finish()


# Handler to delete all pending notifications for specific user
async def delete_notifications(message: types.Message, state: FSMContext):
    user = await u.get_user(message.from_user.id)
    if not user:
        await message.answer(
            "❌ Ты не зарегистрирован в боте! Напиши /start, чтобы зарегистрироваться."
        )
        return
    jobs: List[Job] = await tasks.get_jobs(user)
    if not jobs:
        await message.answer("❌ Ты пока не добавлял день рождения!")
        return
    for job in jobs:
        scheduler.remove_job(job.id)
    await message.answer("✅ Все уведомления о твоем др удалены!")


class SecretForm(StatesGroup):
    user_id = State()
    timestamp = State()
    message = State()


# My goal is to make a secret way to create delayed messages with /secret command
# First step will be id, then user will write timestamp and then message to deliver


async def cancel(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.answer("❌ Отменено!")
    await query.message.delete()


async def secret(message: types.Message, state: FSMContext):
    await SecretForm.user_id.set()
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    markup.add(cancel)

    await message.answer("1/3 - Введи ID пользователя: ", reply_markup=markup)


async def secret_timestamp(message: types.Message, state: FSMContext):
    await SecretForm.next()
    user_id = message.text
    user = await u.get_user(user_id)
    if not user_id.isdigit():
        await message.answer("❌ ID пользователя должен состоять только из цифр!")
        await state.finish()
        return
    if not user:
        await message.answer("❌ Пользователь не зарегистрирован в боте!")
        await state.finish()
        return

    await state.update_data(user_id=int(user_id))
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    markup.add(cancel)

    await message.answer(
        f"2/3 - Пользователь найден: {user.full_name}! Введи timestamp сообщения: ",
        reply_markup=markup,
    )


async def secret_message(message: types.Message, state: FSMContext):
    await SecretForm.next()
    timestamp = message.text
    if not timestamp.isdigit():
        await message.answer("❌ Timestamp должен состоять только из цифр!")
        await state.finish()
        return
    await state.update_data(timestamp=int(timestamp))
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    markup.add(cancel)
    await message.answer("3/3 - Введи сообщение: ", reply_markup=markup)


async def secret_confirm(message: types.Message, state: FSMContext):
    await SecretForm.next()
    data = await state.get_data()
    user_id = data["user_id"]
    timestamp = data["timestamp"]
    message_text = message.text
    await message.answer("✅ Готово!")
    await tasks.schedule_secret_message(user_id, timestamp, message_text)
    await state.finish()
