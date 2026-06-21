from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import engine, get_session
from app import models

app = FastAPI(title="Еврокомиссия API")

@app.get("/")
def read_root():
    return {"message": "Сервер работает!"}

@app.get("/songs/")
def get_all_songs(session: Session = Depends(get_session)):
    statement = select(models.Song)
    songs = session.scalars(statement).all()
    return songs