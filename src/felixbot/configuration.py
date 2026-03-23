from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

dir_path = Path(__file__).parent.parent.parent


class BotSettings(BaseModel):
    token: str


class LoggingSettings(BaseModel):
    level: str
    format: str


class DbSettings(BaseModel):
    host: str
    password: str
    user: str
    db: str
    port: int
    driver: str
    dialect: str = "postgresql"

    @property
    def dsn(self):
        return f"{self.dialect}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseModel):
    host: str
    password: str
    port: int
    db: int


class Config(BaseSettings):
    bot: BotSettings
    logging: LoggingSettings
    postgres: DbSettings
    redis: RedisSettings

    model_config = SettingsConfigDict(
        env_file=dir_path / ".env",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
    )


config = Config()

