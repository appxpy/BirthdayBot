from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command, CommandStart, Text
from magic_filter import F

from bot.handlers.user.commands import AuthForm, auth, cmd_start
from bot.handlers.user.handlers import (
    Form,
    SecretForm,
    cancel,
    create,
    create_confirm,
    create_day,
    create_month,
    create_preference,
    create_preference_back,
    delete_notifications,
    jobs,
    secret,
    secret_confirm,
    secret_message,
    secret_timestamp,
)


async def setup(dp: Dispatcher):
    # Commands
    dp.register_message_handler(cmd_start, CommandStart(""), state="*")
    dp.register_message_handler(jobs, Text("Список напоминаний 📝"), state="*")
    dp.register_message_handler(
        create_month, Text("Добавить день рождения 🎂"), state="*"
    )
    dp.register_callback_query_handler(create_day, state=Form.month)
    dp.register_message_handler(
        delete_notifications, Text("Удалить день рождения ❌"), state="*"
    )
    dp.register_callback_query_handler(create_preference, state=Form.day)
    dp.register_callback_query_handler(create_preference_back, state=Form.preference)
    dp.register_message_handler(create, state=Form.preference)
    dp.register_callback_query_handler(create_confirm, state=Form.confirm)
    dp.register_message_handler(auth, state=AuthForm.password)

    dp.register_message_handler(secret, Command("secret"), state="*")
    dp.register_callback_query_handler(
        cancel, F.data == "cancel", state=SecretForm.all_states
    )
    dp.register_message_handler(secret_timestamp, state=SecretForm.user_id)
    dp.register_message_handler(secret_message, state=SecretForm.timestamp)
    dp.register_message_handler(secret_confirm, state=SecretForm.message)
