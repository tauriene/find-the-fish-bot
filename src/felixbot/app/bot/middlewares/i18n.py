import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

logger = logging.getLogger(__name__)


class I18nMiddleware(BaseMiddleware):
    def __init__(self, hub: TranslatorHub):
        self.hub = hub

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        locale = "en"

        if user and user.language_code == "ru":
            locale = "ru"

        data["i18n"] = self.hub.get_translator_by_locale(locale)
        return await handler(event, data)
