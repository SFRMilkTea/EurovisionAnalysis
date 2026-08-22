from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Данные для публичной регистрации обычного пользователя."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=3, max_length=72)


# Что админ отправляет на сервер для создания юзера
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=3, max_length=72)
    is_admin: bool = False


# Что сервер отдает обратно (ОБЯЗАТЕЛЬНО БЕЗ пароля!)
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool
