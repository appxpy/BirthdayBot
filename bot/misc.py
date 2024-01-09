import asyncio
from pathlib import Path

import pytz
from aiogram import Bot, Dispatcher
from AiogramStorages.storages import PGStorage
from aiogram.utils.executor import Executor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

import config

ROOT_DIR: Path = Path(__file__).parent.parent

loop = asyncio.get_event_loop()
storage = PGStorage(
    username=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    host=config.POSTGRES_HOST,
    port=config.POSTGRES_PORT,
    db_name=config.POSTGRES_DB,
)

jobstores = {
    "default": SQLAlchemyJobStore(
        url=f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}",
        tablename="birthday_jobs",
    )
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=pytz.timezone("Europe/Moscow"),
    job_defaults={"misfire_grace_time": 24 * 60 * 60},
)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot=bot, loop=loop, storage=storage)

executor = Executor(dp, skip_updates=True)


async def setup():
    user = await bot.me
    logger.info(f"Bot: {user.full_name} [@{user.username}]")
    logger.debug(f"{ROOT_DIR=}")
