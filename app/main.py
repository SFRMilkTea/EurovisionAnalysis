from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.security import verify_password, create_access_token
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pathlib import Path
from app.database import get_session
from app import models
from app.deps import get_current_admin
from app.schemas import UserCreate, UserRead, UserRegister
from app.users import create_user

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app/templates"))

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    songs = session.scalars(select(models.Song).options(selectinload(models.Song.country))).all()
    users = session.scalars(select(models.User)).all()
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.scalars(
        select(models.User).where(models.User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, session: Session = Depends(get_session),):
    return create_user(session, user_in, is_admin=False)


@app.post("/admin/users/", response_model=UserRead)
def admin_create_user(
        user_in: UserCreate,
        session: Session = Depends(get_session),
        current_admin: models.User = Depends(get_current_admin)  # <-- Пускает только админов
):
    return create_user(session, user_in, is_admin=user_in.is_admin)
