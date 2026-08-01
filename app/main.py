from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.security import verify_password, create_access_token, get_password_hash
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pathlib import Path
from app.database import get_session
from app import models
from app.deps import get_current_admin
from app.schemas import UserCreate, UserRead

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app/templates"))

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    # 1. Получаем все песни И СРАЗУ подтягиваем страны
    songs = session.scalars(
        select(models.Song).options(selectinload(models.Song.country))
    ).all()

    # 2. Получаем всех юзеров (чтобы построить колонки)
    users = session.scalars(select(models.User)).all()

    # 3. Получаем все оценки и складываем в удобный словарь:
    # {(song_id, user_id, stage): Opinion}
    all_opinions = session.scalars(select(models.Opinion)).all()
    opinions_map = {}
    for op in all_opinions:
        opinions_map[(op.song_id, op.user_id, op.stage.value)] = op

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "songs": songs,
            "users": users,
            "opinions_map": opinions_map
        }
    )


@app.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    # 1. Ищем юзера в базе по username (который вводится в форме)
    user = session.scalars(
        select(models.User).where(models.User.username == form_data.username)
    ).first()

    # 2. Если юзера нет ИЛИ пароль не совпадает — выдаем ошибку
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Если всё ок — создаем JWT-токен
    access_token = create_access_token(subject=user.id)

    # 4. Возвращаем токен в формате, который ждет Swagger
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/admin/users/", response_model=UserRead)
def admin_create_user(
        user_in: UserCreate,
        session: Session = Depends(get_session),
        current_admin: models.User = Depends(get_current_admin)  # <-- Пускает только админов
):
    # 1. Проверяем, не занят ли email
    existing_user = session.scalars(
        select(models.User).where(models.User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # 2. Хэшируем пароль
    hashed_password = get_password_hash(user_in.password)

    # 3. Создаем юзера
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_password,
        is_admin=user_in.is_admin
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
