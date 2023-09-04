from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.controllers import user as u
from bot.markups import reply_markups
from bot.misc import bot


class AuthForm(StatesGroup):
    password = State()


async def menu(message: types.Message, state: FSMContext):
    await message.answer(
        "Не удаляй это сообщение. Оно нужно для отображения меню снизу.",
        reply_markup=reply_markups.menu(),
    )
    await bot.send_message(
        message.from_user.id,
        "Вот небольшая инструкция:\n\n 1. Тебе нужно добавить свой день рождения (если ты еще этого не делал). Для этого воспользуйся кнопкой <b>Добавить день рождения 🎂</b>.\n\n2. Посмотреть будущие напоминания - кнопка <b>Список напоминаний 📝</b>\n\n3. Ты устал от человеческого общества и хочешь всем язвить что все забыли про твой др? Кнопка <b>Удалить день рождения ❌</b> для тебя.\n\nвроде все..",
    )


async def cmd_start(message: types.Message, state: FSMContext):
    user = await u.get_user(message.from_user.id)
    await state.finish()
    if not user:
        await bot.send_message(
            message.from_user.id,
            text=f"Привет <b>{message.from_user.full_name}</b>!\n\nЯ бот, который будет отправлять тебе информацию о днях рождения твоих друзей <span class='tg-spoiler'>(ну или почти)</span>.\n\nКороче, тебе сейчас надо будет отправить в чат <b>пароль</b>, чтобы я мог понять что ты это ты.\n\nЕсли будут какие-то проблемы, то пиши @appxpy",
            parse_mode="HTML",
        )
        await AuthForm.password.set()
    else:
        await menu(message, state)


async def auth(message: types.Message, state: FSMContext):
    if message.text.lower() == "БМВМ4":
        await message.answer("Пароль верный!")
        await u.create_user(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username,
        )
        await menu(message, state)
    else:
        await message.answer("Пароль неверный! Попробуй еще раз.")
        await AuthForm.password.set()
    await message.delete()
