from typing import Optional
import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from alembic import op
import sqlalchemy as sa
from config import settings
import uvicorn


from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    create_engine,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_dz_2")

DATABASE_URL = settings.sqlalchemy_uri
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    adopted = Column(Boolean, default=False, nullable=False)
    health_status = Column(String(50), default="healthy", nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)


# Base.metadata.create_all(bind=engine)

class AnimalResponse(BaseModel):
    id: int
    name: str
    age: int
    adopted: bool
    health_status: str

    class Config:
        orm_mode = True


class AnimalCreate(BaseModel):
    name: str = Field(..., example="Рекс")
    age: int = Field(..., example=3)
    adopted: bool = False
    health_status: str = "healthy"

    @validator("age")
    def age_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Вік не може бути від’ємним.")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


app = FastAPI(title="FastAPI - animals & tasks example")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/animals/", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
def create_animal(payload: AnimalCreate):
    if payload.age < 0:
        logger.error("Create animal failed: negative age=%s", payload.age)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вік не може бути від’ємним.")
    db = SessionLocal()
    try:
        animal = Animal(
            name=payload.name,
            age=payload.age,
            adopted=payload.adopted,
            health_status=payload.health_status or "healthy",
        )
        db.add(animal)
        db.commit()
        db.refresh(animal)
        return animal
    finally:
        db.close()


@app.get("/animals/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int):
    db = SessionLocal()
    try:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            logger.error("Animal not found: id=%s", animal_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Тварину з id={animal_id} не знайдено.")
        if animal.age < 0:
            logger.error("Animal has negative age in DB: id=%s, age=%s", animal_id, animal.age)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вік не може бути від’ємним.")
        return animal
    finally:
        db.close()


@app.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    db = SessionLocal()
    try:
        task = Task(title=payload.title, description=payload.description)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    finally:
        db.close()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    if task_id > 1000:
        logger.error("Task id out of allowed range: %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task id перевищує допустимий максимум (1000).",
        )

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error("Task not found: id=%s", task_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задачу з id={task_id} не знайдено.")
        return task
    finally:
        db.close()


@app.get("/animals/", response_model=list[AnimalResponse])
def list_animals():
    db = SessionLocal()
    try:
        animals = db.query(Animal).all()
        return animals
    finally:
        db.close()

if __name__ == "__main__":
   uvicorn.run("main_dz_2:app")