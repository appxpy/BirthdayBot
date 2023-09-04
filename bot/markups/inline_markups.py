from ast import In

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

months = [
    [("Январь", 1), ("Февраль", 2), ("Март", 3)],
    [("Апрель", 4), ("Май", 5), ("Июнь", 6)],
    [("Июль", 7), ("Август", 8), ("Сентябрь", 9)],
    [("Октябрь", 10), ("Ноябрь", 11), ("Декабрь", 12)],
]

month_days = {
    1: 31,
    2: 28,  # ну если весокосный год то пиздец
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}


def month_select():
    markup = InlineKeyboardMarkup(resize_keyboard=False, row_width=3)
    for row in months:
        markup.row(
            *[InlineKeyboardButton(item[0], callback_data=item[1]) for item in row]
        )
    markup.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return markup


def day_select(month: int):
    days = month_days.get(month, 28)
    markup = InlineKeyboardMarkup(resize_keyboard=False, row_width=7)
    markup.add(
        InlineKeyboardButton(
            months[(month - 1) // 3][(month - 1) % 3][0], callback_data="ignore"
        )
    )
    for k in range((days - 1) // 7 + 1):
        row_buttons = []
        for i in range(7):
            day_number = k * 7 + i + 1
            if day_number <= days:
                row_buttons.append(
                    InlineKeyboardButton(str(day_number), callback_data=str(day_number))
                )
            else:
                row_buttons.append(
                    InlineKeyboardButton(
                        " ", callback_data="ignore", callback_game="ignore"
                    )
                )
        markup.row(*row_buttons)
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return markup


def back():
    return InlineKeyboardMarkup(resize_keyboard=False, row_width=1).add(
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )


def confirmation():
    return InlineKeyboardMarkup(resize_keyboard=False, row_width=1).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel"),
    )
