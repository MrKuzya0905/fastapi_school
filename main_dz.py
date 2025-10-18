from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, field_validator
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import uvicorn

DATABASE_URL = "sqlite:///./participants.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI(title="Participants API")


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (UniqueConstraint("email", name="uq_participant_email"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    event = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ParticipantCreate(BaseModel):
    name: str
    email: EmailStr
    event: str
    age: int

    @field_validator('name')
    def validate_name(cls, value: str) -> str:
        if any(char.isdigit() for char in value):
            raise ValueError("Ім'я не повинно містити цифр")
        return value
    
    @field_validator('age')
    def validate_age(cls, value: int) -> int:
        if not (12 <= value <= 120):
            raise ValueError("Вік має бути від 12 до 120")
        return value


class ParticipantOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    event: str
    age: int

    class Config:
        orm_mode = True


@app.post("/participants/", response_model=ParticipantOut, status_code=status.HTTP_201_CREATED)
def create_participant(payload: ParticipantCreate, db: Session = Depends(get_db)):
    existing = db.query(Participant).filter(Participant.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email вже зареєстровано")

    participant = Participant(
        name=payload.name.strip(),
        email=payload.email,
        event=payload.event.strip(),
        age=payload.age,
    )
    db.add(participant)
    try:
        db.commit()
        db.refresh(participant)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email вже зареєстровано")

    return participant


@app.get("/participants/event/{event_name}", response_model=List[ParticipantOut])
def get_participants_by_event(event_name: str, db: Session = Depends(get_db)):
    participants = db.query(Participant).filter(Participant.event == event_name).all()
    return participants


if __name__ == "__main__":

    uvicorn.run("main_dz:app", reload=True)