import os
from pathlib import Path, PurePath

from pydantic import BaseSettings

dir_path = Path(__file__).resolve().parent.parent
env_file_name = '.env'
env_path = PurePath(dir_path, env_file_name)


class Settings(BaseSettings):
    """Получение базовых настроек из переменных окружения"""
    MODE: str
    SECRET_KEY: str

    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @property
    def SQL_URL(self) -> str:
        return (f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/'
                f'{self.POSTGRES_DB}')

    @property
    def ASYNC_SQL_URL(self) -> str:
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/'
                f'{self.POSTGRES_DB}')

    #TODO переделать настройки для подключения через .test.env
    @property
    def ASYNC_TEST_SQL_URL(self) -> str:
        return (f'postgresql+asyncpg://postgres:postgres@localhost:5433/notes-test')

    class Config:
        env_file = env_path
        allow_mutation = False


settings = Settings()
