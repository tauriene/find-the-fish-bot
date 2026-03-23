from felixbot.configuration import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(url=config.postgres.dsn, echo=True)

sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
