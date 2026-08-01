import getpass
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import engine
from app import models
from app.security import get_password_hash

def create_admin():
    print("=== Создание учетной записи Администратора ===")
    username = input("Введите username: ")
    email = input("Введите email: ")
    password = getpass.getpass("Введите пароль: ")

    with Session(engine) as session:
        # Проверяем, нет ли уже юзера с таким email
        existing = session.scalars(select(models.User).where(models.User.email == email)).first()
        if existing:
            print("Пользователь с таким email уже существует!")
            return

        # Хэшируем пароль и создаем юзера
        hashed_password = get_password_hash(password)
        admin_user = models.User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_admin=True,
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        print(f"✅ Админ {username} успешно создан!")

if __name__ == "__main__":
    create_admin()