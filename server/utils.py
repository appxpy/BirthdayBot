import asyncio
from decimal import Decimal
from typing import Union

from aiogram.utils import exceptions
from loguru import logger

from bot.misc import bot, config
from bot.models import User


async def send_message_to_payments_chat(amount: Decimal, worker: Union[User, None]):
    pass
