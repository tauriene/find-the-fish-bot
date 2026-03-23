import asyncio
import logging

from felixbot.app.bot import main
from felixbot.configuration import config

logging.basicConfig(level=config.logging.level, format=config.logging.format)

logger = logging.getLogger(__name__)

try:
    asyncio.run(main())
except KeyboardInterrupt, SystemExit:
    logger.info("Bot stopped")
