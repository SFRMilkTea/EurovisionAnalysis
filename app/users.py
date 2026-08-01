from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.schemas import UserCreate, UserRegister
from app.security import get_password_hash


def create_user(
        session: Session,
        user_in: UserRegister | UserCreate,
        *,
        is_admin: bool = False,
) -> models.User:
    existing_user = session.scalars(
        select(models.User).where(
            or_(
                models.User.email == user_in.email,
            )
        )
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {user_in.email} уже зарегистрирован",
        )

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_admin=is_admin,
        is_active=True,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Логин или email уже зарегистрирован",
        )

    session.refresh(user)
    return user
