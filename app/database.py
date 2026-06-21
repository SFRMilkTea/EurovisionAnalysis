from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from fastapi import Depends # Понадобится для зависимости в FastAPI

# Твои красивые соглашения об именах
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

# --- ДОБАВЛЯЕМ ПОДКЛЮЧЕНИЕ ---

# Строка подключения (замени пароль и название БД на свои)
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/eurovision_analysis"

# Создаем движок. echo=True покажет SQL-запросы в терминале — очень удобно дебажить!
engine = create_engine(DATABASE_URL, echo=True)

# Функция, которую будет использовать FastAPI
def get_session():
    with Session(engine) as session:
        yield session