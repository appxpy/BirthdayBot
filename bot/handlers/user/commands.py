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
        await bot.send_photo(
            message.from_user.id,
            photo="https://downloader.disk.yandex.ru/preview/9d2d891eff5bdcbdf739cadea92fd663ac48550ab2f6b821950e37fdbb409989/64f62acb/xHT-fWY39LZs91HLXcfEWxQb2qQ4HXsPCPcN-Z9kMmNa5E03ZZHv2VTCL8xQdqongPdOZGWMyGrV8cfcdGCpng%3D%3D?uid=0&filename=%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202023-09-04%20%D0%B2%2018.06.16.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&tknv=v2&size=2048x2048",
            caption=f"Привет <b>{message.from_user.full_name}</b>!\n\nЯ бот, который будет отправлять тебе информацию о днях рождения твоих друзей <span class='tg-spoiler'>(ну или почти)</span>.\n\nКороче, тебе сейчас надо будет отправить в чат <b>пароль</b>, чтобы я мог понять что ты это ты. Паролем будет служить решение этого многомерного интеграла (точность 3 знака после запятой в формате <i>1,234</i>)\n\nЕсли будут какие-то проблемы, то пиши @appxpy",
            parse_mode="HTML",
        )
        await AuthForm.password.set()
    else:
        await menu(message, state)


async def auth(message: types.Message, state: FSMContext):
    if message.text.lower() == "иди нахуй":
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
