from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.config import settings
from app.database import get_session
from app.deps import get_current_admin
from app.schemas import UserCreate, UserRead, UserRegister
from app.security import create_access_token, verify_password
from app.users import create_user

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app/templates"))

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


def get_current_user(request: Request, session: Session) -> models.User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = session.get(models.User, user_id)
    if user is None or not user.is_active:
        request.session.clear()
        return None
    return user


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    session: Session = Depends(get_session),
):
    user = session.scalars(select(models.User).where(models.User.email == email)).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Неверный логин или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user.last_login_at = datetime.now(timezone.utc)
    session.commit()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/token")
def create_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.scalars(
        select(models.User).where(models.User.username == form_data.username)
    ).first()
    if not user or not user.is_active or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(subject=user.id), "token_type": "bearer"}


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    event_id: int | None = None,
    session: Session = Depends(get_session),
):
    current_user = get_current_user(request, session)
    if current_user is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    events = session.scalars(
        select(models.Event).order_by(models.Event.year.desc(), models.Event.name)
    ).all()
    selected_event = next((event for event in events if event.id == event_id), None)
    if selected_event is None and events:
        selected_event = events[0]

    songs_query = select(models.Song).options(selectinload(models.Song.country))
    if selected_event is not None:
        songs_query = songs_query.where(models.Song.event_id == selected_event.id)
    else:
        songs_query = songs_query.where(models.Song.event_id.is_(None))
    songs = session.scalars(songs_query).all()
    users = session.scalars(select(models.User)).all()
    opinions_map = {
        (op.song_id, op.user_id, op.stage.value): op
        for op in session.scalars(select(models.Opinion)).all()
    }
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "songs": songs,
            "events": events,
            "selected_event": selected_event,
            "users": users,
            "opinions_map": opinions_map,
            "current_user": current_user,
        },
    )


@app.post("/opinions/save")
def save_opinion(
    request: Request,
    song_id: int = Form(),
    event_id: int | None = Form(default=None),
    stage: models.Stage = Form(),
    score: int = Form(),
    note: str | None = Form(default=None),
    session: Session = Depends(get_session),
):
    current_user = get_current_user(request, session)
    if current_user is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    if score not in {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Недопустимая оценка")
    song = session.get(models.Song, song_id)
    if song is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Песня не найдена")
    if event_id is not None and song.event_id != event_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Песня не относится к мероприятию",
        )

    opinion = session.scalars(
        select(models.Opinion).where(
            models.Opinion.song_id == song_id,
            models.Opinion.user_id == current_user.id,
            models.Opinion.stage == stage,
        )
    ).first()
    if opinion is None:
        opinion = models.Opinion(song_id=song_id, user_id=current_user.id, stage=stage, score=score)
        session.add(opinion)
    opinion.score = score
    opinion.note = note.strip() or None if note else None
    session.commit()
    redirect_url = f"/?event_id={event_id}" if event_id is not None else "/"
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, session: Session = Depends(get_session)):
    return create_user(session, user_in, is_admin=False)


@app.post("/admin/users/", response_model=UserRead)
def admin_create_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
    current_admin: models.User = Depends(get_current_admin),
):
    return create_user(session, user_in, is_admin=user_in.is_admin)
