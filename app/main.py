from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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


def require_session_admin(request: Request, session: Session) -> models.User:
    """Проверяет роль администратора для страниц, работающих через cookie-сессию."""
    user = get_current_user(request, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ только для администраторов")
    return user


def can_manage_admin(request: Request, session: Session) -> bool:
    """Временно оставляет панель открытой для первоначального создания администратора."""
    return True


def set_admin_message(request: Request, text: str, kind: str = "success") -> None:
    request.session["admin_message"] = {"text": text, "kind": kind}


def admin_redirect(request: Request) -> RedirectResponse:
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


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
    # if current_user is None:
    #     return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    events = session.scalars(
        select(models.Event).order_by(models.Event.year.desc(), models.Event.name)
    ).all()
    selected_event = next((event for event in events if event.id == event_id), None)
    if selected_event is None:
        selected_event = next((event for event in events if event.id == 2), None)
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


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, edit: str | None = None, session: Session = Depends(get_session)):
    current_user = get_current_user(request, session)
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    message = request.session.pop("admin_message", None)
    countries = session.scalars(select(models.Country).order_by(models.Country.name)).all()
    events = session.scalars(select(models.Event).options(selectinload(models.Event.host)).order_by(models.Event.year.desc())).all()
    genres = session.scalars(select(models.Genre).order_by(models.Genre.name)).all()
    languages = session.scalars(select(models.Language).order_by(models.Language.name)).all()
    users = session.scalars(select(models.User).order_by(models.User.username)).all()
    songs = session.scalars(
        select(models.Song).options(selectinload(models.Song.country), selectinload(models.Song.event)).order_by(models.Song.year.desc(), models.Song.name)
    ).all()
    song_genres = {}
    for link in session.scalars(select(models.SongGenre)).all():
        song_genres.setdefault(link.song_id, set()).add(link.genre_id)
    song_languages = {}
    for link in session.scalars(select(models.SongLanguage)).all():
        song_languages.setdefault(link.song_id, set()).add(link.language_id)
    return templates.TemplateResponse(request, "admin.html", {
        "current_user": current_user, "message": message, "countries": countries,
        "events": events, "genres": genres, "languages": languages, "songs": songs, "users": users,
        "vocals": list(models.Vocal), "edit": edit,
        "song_genres": song_genres, "song_languages": song_languages,
    })


@app.post("/admin/countries")
def admin_create_country(request: Request, name: str = Form(), session: Session = Depends(get_session)):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    name = name.strip()
    if not name:
        set_admin_message(request, "Название страны не может быть пустым.", "error")
    else:
        try:
            session.add(models.Country(name=name))
            session.commit()
            set_admin_message(request, "Страна добавлена.")
        except IntegrityError:
            session.rollback()
            set_admin_message(request, "Такая страна уже есть.", "error")
    return admin_redirect(request)


@app.post("/admin/events")
def admin_create_event(request: Request, name: str = Form(), year: int = Form(), host_id: int = Form(), session: Session = Depends(get_session)):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    if not name.strip() or not session.get(models.Country, host_id):
        set_admin_message(request, "Укажите название мероприятия и страну-хозяйку.", "error")
    else:
        session.add(models.Event(name=name.strip(), year=year, host_id=host_id))
        session.commit()
        set_admin_message(request, "Мероприятие добавлено.")
    return admin_redirect(request)


@app.post("/admin/catalog/{catalog_name}")
def admin_create_catalog_item(request: Request, catalog_name: str, name: str = Form(), session: Session = Depends(get_session)):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    model = {"genres": models.Genre, "languages": models.Language}.get(catalog_name)
    if model is None:
        raise HTTPException(status_code=404)
    name = name.strip()
    if not name:
        set_admin_message(request, "Название не может быть пустым.", "error")
        return admin_redirect(request)
    try:
        session.add(model(name=name))
        session.commit()
        set_admin_message(request, "Запись добавлена.")
    except IntegrityError:
        session.rollback()
        set_admin_message(request, "Такая запись уже есть или название пустое.", "error")
    return admin_redirect(request)


@app.post("/admin/songs")
def admin_create_song(
    request: Request, country_id: int = Form(), event_id: int | None = Form(default=None),
    year: int = Form(), name: str = Form(), artist: str = Form(), vocal: models.Vocal = Form(),
    bpm: int | None = Form(default=None), key: str | None = Form(default=None), energy: int | None = Form(default=None),
    danceability: int | None = Form(default=None), happiness: int | None = Form(default=None), url: str | None = Form(default=None),
    genre_ids: list[int] = Form(default=[]), language_ids: list[int] = Form(default=[]), session: Session = Depends(get_session),
):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    valid_metrics = all(value is None or 0 <= value <= 100 for value in (energy, danceability, happiness))
    if not name.strip() or not artist.strip() or not session.get(models.Country, country_id) or not valid_metrics:
        set_admin_message(request, "Проверьте обязательные поля и значения характеристик (0–100).", "error")
        return admin_redirect(request)
    if event_id is not None and not session.get(models.Event, event_id):
        set_admin_message(request, "Выбрано несуществующее мероприятие.", "error")
        return admin_redirect(request)
    song = models.Song(country_id=country_id, event_id=event_id, year=year, name=name.strip(), artist=artist.strip(), vocal=vocal,
                       bpm=bpm, key=key.strip() or None if key else None, energy=energy, danceability=danceability,
                       happiness=happiness, url=url.strip() or None if url else None)
    session.add(song)
    session.flush()
    for genre_id in set(genre_ids):
        if session.get(models.Genre, genre_id):
            session.add(models.SongGenre(song_id=song.id, genre_id=genre_id))
    for language_id in set(language_ids):
        if session.get(models.Language, language_id):
            session.add(models.SongLanguage(song_id=song.id, language_id=language_id))
    session.commit()
    set_admin_message(request, "Песня добавлена.")
    return admin_redirect(request)


@app.post("/admin/{entity}/{item_id}/delete")
def admin_delete_item(request: Request, entity: str, item_id: int, session: Session = Depends(get_session)):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    model = {"countries": models.Country, "events": models.Event, "genres": models.Genre, "languages": models.Language, "songs": models.Song}.get(entity)
    if model is None:
        raise HTTPException(status_code=404)
    item = session.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404)
    try:
        session.delete(item)
        session.commit()
        set_admin_message(request, "Запись удалена.")
    except IntegrityError:
        session.rollback()
        set_admin_message(request, "Не удалось удалить запись: она используется в других данных.", "error")
    return admin_redirect(request)


@app.post("/admin/users")
def admin_create_user_from_page(
    request: Request,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    is_admin: bool = Form(default=False),
    session: Session = Depends(get_session),
):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    try:
        create_user(session, UserCreate(username=username, email=email, password=password, is_admin=is_admin), is_admin=is_admin)
        set_admin_message(request, "Пользователь создан.")
    except (HTTPException, ValueError, IntegrityError):
        session.rollback()
        set_admin_message(request, "Не удалось создать пользователя. Проверьте уникальность логина и почты.", "error")
    return admin_redirect(request)


def is_last_active_admin(user: models.User, session: Session) -> bool:
    """Не позволяет оставить систему без администратора."""
    if not (user.is_admin and user.is_active):
        return False
    active_admins = session.scalars(
        select(models.User).where(models.User.is_admin.is_(True), models.User.is_active.is_(True))
    ).all()
    return len(active_admins) <= 1


@app.post("/admin/users/{user_id}/update")
def admin_update_user(
    request: Request,
    user_id: int,
    username: str = Form(),
    is_admin: bool = Form(default=False),
    is_active: bool = Form(default=False),
    session: Session = Depends(get_session),
):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    user = session.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    username = username.strip()
    if not 3 <= len(username) <= 50:
        set_admin_message(request, "Логин должен содержать от 3 до 50 символов.", "error")
        return admin_redirect(request)
    same_name_user = session.scalars(
        select(models.User).where(models.User.username == username, models.User.id != user.id)
    ).first()
    if same_name_user:
        set_admin_message(request, "Этот логин уже занят.", "error")
        return admin_redirect(request)
    if is_last_active_admin(user, session) and (not is_admin or not is_active):
        set_admin_message(request, "Нельзя снять права или отключить последнего активного администратора.", "error")
        return admin_redirect(request)
    user.username = username
    user.is_admin = is_admin
    user.is_active = is_active
    session.commit()
    set_admin_message(request, "Права пользователя обновлены.")
    return admin_redirect(request)


@app.post("/admin/users/{user_id}/delete")
def admin_delete_user(request: Request, user_id: int, session: Session = Depends(get_session)):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    user = session.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if is_last_active_admin(user, session):
        set_admin_message(request, "Нельзя удалить последнего активного администратора.", "error")
        return admin_redirect(request)
    session.delete(user)
    session.commit()
    set_admin_message(request, "Пользователь удалён.")
    return admin_redirect(request)


@app.post("/admin/{entity}/{item_id}/update")
def admin_update_item(
    request: Request, entity: str, item_id: int,
    name: str | None = Form(default=None), year: int | None = Form(default=None), host_id: int | None = Form(default=None),
    country_id: int | None = Form(default=None), event_id: int | None = Form(default=None), artist: str | None = Form(default=None),
    vocal: models.Vocal | None = Form(default=None), bpm: int | None = Form(default=None), key: str | None = Form(default=None),
    energy: int | None = Form(default=None), danceability: int | None = Form(default=None), happiness: int | None = Form(default=None),
    url: str | None = Form(default=None), genre_ids: list[int] = Form(default=[]), language_ids: list[int] = Form(default=[]),
    session: Session = Depends(get_session),
):
    if not can_manage_admin(request, session):
        require_session_admin(request, session)
    model = {"countries": models.Country, "genres": models.Genre, "languages": models.Language, "events": models.Event, "songs": models.Song}.get(entity)
    item = session.get(model, item_id) if model else None
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if entity in {"countries", "genres", "languages"}:
        if not name or not name.strip():
            set_admin_message(request, "Название не может быть пустым.", "error")
            return RedirectResponse(f"/admin?edit={entity}", status_code=303)
        item.name = name.strip()
    elif entity == "events":
        if not name or year is None or not host_id or not session.get(models.Country, host_id):
            set_admin_message(request, "Проверьте поля мероприятия.", "error")
            return RedirectResponse("/admin?edit=events", status_code=303)
        item.name, item.year, item.host_id = name.strip(), year, host_id
    else:
        metrics = (energy, danceability, happiness)
        if not name or not artist or not country_id or year is None or vocal is None or not session.get(models.Country, country_id) or any(v is not None and not 0 <= v <= 100 for v in metrics):
            set_admin_message(request, "Проверьте обязательные поля песни и значения 0–100.", "error")
            return RedirectResponse("/admin?edit=songs", status_code=303)
        if event_id is not None and not session.get(models.Event, event_id):
            set_admin_message(request, "Выбрано несуществующее мероприятие.", "error")
            return RedirectResponse("/admin?edit=songs", status_code=303)
        item.country_id, item.event_id, item.year, item.name, item.artist, item.vocal = country_id, event_id, year, name.strip(), artist.strip(), vocal
        item.bpm, item.key, item.energy, item.danceability, item.happiness = bpm, key.strip() or None if key else None, energy, danceability, happiness
        item.url = url.strip() or None if url else None
        session.query(models.SongGenre).filter_by(song_id=item.id).delete()
        session.query(models.SongLanguage).filter_by(song_id=item.id).delete()
        for genre_id in set(genre_ids):
            if session.get(models.Genre, genre_id): session.add(models.SongGenre(song_id=item.id, genre_id=genre_id))
        for language_id in set(language_ids):
            if session.get(models.Language, language_id): session.add(models.SongLanguage(song_id=item.id, language_id=language_id))
    try:
        session.commit()
        set_admin_message(request, "Запись обновлена.")
    except IntegrityError:
        session.rollback()
        set_admin_message(request, "Не удалось сохранить: значение должно быть уникальным.", "error")
    return RedirectResponse(f"/admin?edit={entity}", status_code=303)


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
        return JSONResponse({"detail": "Требуется вход"}, status_code=status.HTTP_401_UNAUTHORIZED)
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
    return {"ok": True}


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
