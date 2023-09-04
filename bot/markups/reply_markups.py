from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Main menu with emojis
    # 1. Добавить день рождения 🎂
    # 2. Список напоминаний 📝
    # 3. Удалить день рождения ❌

    markup.row(KeyboardButton("Добавить день рождения 🎂"))
    markup.row(KeyboardButton("Список напоминаний 📝"))
    markup.row(KeyboardButton("Удалить день рождения ❌"))
    return markup
