import logging

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from redis.asyncio import Redis
from fluentogram import TranslatorHub

from felixbot.app.bot.middlewares.i18n import I18nMiddleware
from felixbot.app.bot.middlewares.session import DbSessionMiddleware
from felixbot.app.i18n import create_translator_hub
from felixbot.app.infrastructure.db import sessionmaker
from felixbot.app.infrastructure.redis import RedisRepo
from felixbot.configuration import config
from felixbot.app.bot.handlers import routers
from aiogram import Bot, Dispatcher

logger = logging.getLogger(__name__)


async def set_ui_commands(bot: Bot, hub: TranslatorHub):
    i18n = hub.get_translator_by_locale("ru")
    await bot.set_my_commands(
        [
            BotCommand(command="start", description=i18n.start.desc()),
            BotCommand(command="profile", description=i18n.profile.desc()),
            BotCommand(command="game", description=i18n.game.desc()),
            BotCommand(command="top", description=i18n.top.desc()),
            BotCommand(command="stop", description=i18n.stop.desc()),
            BotCommand(command="mygames", description=i18n.mygames.desc()),
        ],
        BotCommandScopeDefault(),
        language_code="ru",
    )

    i18n = hub.get_translator_by_locale("en")
    await bot.set_my_commands(
        [
            BotCommand(command="start", description=i18n.start.desc()),
            BotCommand(command="profile", description=i18n.profile.desc()),
            BotCommand(command="game", description=i18n.game.desc()),
            BotCommand(command="top", description=i18n.top.desc()),
            BotCommand(command="stop", description=i18n.stop.desc()),
            BotCommand(command="mygames", description=i18n.mygames.desc()),
        ],
        BotCommandScopeDefault(),
    )


async def main():
    redis = Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db, password=config.redis.password,
                  decode_responses=True)

    storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    redis_repo = RedisRepo(redis)

    bot = Bot(config.bot.token)
    dp = Dispatcher(storage=storage)
    translator_hub: TranslatorHub = create_translator_hub()

    dp.include_routers(*routers)

    dp.message.middleware(DbSessionMiddleware(sessionmaker))
    dp.callback_query.middleware(DbSessionMiddleware(sessionmaker))

    dp.message.middleware(I18nMiddleware(translator_hub))
    dp.callback_query.middleware(I18nMiddleware(translator_hub))

    await set_ui_commands(bot, translator_hub)
    try:
        logger.info("Starting up bot")
        await dp.start_polling(bot, redis_repo=redis_repo)
    except Exception as e:
        logger.exception(e)
