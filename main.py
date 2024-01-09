from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
from loguru import logger

import config
from bot import database, handlers, logging, misc
from bot.misc import dp, executor, scheduler
from server import server


async def on_startup(web_app: web.Application):
    await logging.setup()
    await misc.setup()
    await database.setup()
    scheduler.start()
    logger.info(
        ",".join([f"({i.name} {i.trigger.run_date})" for i in scheduler.get_jobs()])
    )

    logger.info("Configure webhook...")
    await dp.bot.delete_webhook()
    if config.WEBHOOK_USE:
        await dp.bot.set_webhook(config.WEBHOOK_URL)

    logger.info("Configure handlers...")
    await handlers.setup(dp)


async def on_shutdown(web_app: web.Application):
    await dp.bot.delete_webhook()


def main():
    web_app = get_new_configured_app(dispatcher=dp, path=config.WEBHOOK_PATH)
    if config.WEBHOOK_USE:
        web_app.on_startup.append(on_startup)
        web_app.on_shutdown.append(on_shutdown)
        web_app = server.init_app(web_app)
        web.run_app(web_app, **config.WEBHOOK_SERVER, access_log=logger)
    else:
        executor.on_startup(on_startup)
        executor.on_shutdown(on_shutdown)
        executor.start_polling()


if __name__ == "__main__":
    main()
