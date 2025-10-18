from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

Base = declarative_base()
engine = create_async_engine(settings.sqlalchemy_uri, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Cabinet(Base):
    __tablename__ = "cabinets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = String(length=20)
    number: Mapped[int] = mapped_column(Integer())
    students: Mapped[List["Student"]] = relationship(back_populates="cabinet", lazy="selectin")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(length=20))
    cabinet_id: Mapped[int] = mapped_column(ForeignKey(Cabinet.id, ondelete="cascade"))
    cabinet: Mapped[Cabinet] = relationship(back_populates="students", lazy="selectin")


async def create_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with Session() as session:
        yield session
        