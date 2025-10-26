import asyncio, uvicorn
from typing import Optional, List, Annotated

from fastapi import FastAPI, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel, Field

from models import create_db, get_db, Cabinet, Student
from pydantic_models import CabinetModel, CabinetResponseModel, StudentModel, StudentResponseModel

app = FastAPI()

@app.post("/cabinets/", response_model=CabinetResponseModel, status_code=status.HTTP_201_CREATED)
async def add_cabinet(cabinet_model: CabinetModel, 
                      db: Annotated[AsyncSession, Depends(get_db)]
                      ):
    # query1 = select(Cabinet).filter_by(name=cabinet_model.name)
    # query2 = select(Cabinet).filter_by(number=cabinet_model.number)
    # cabinet1 = await db.scalar(query1)
    # cabinet2 = await db.scalar(query2)
    query = select(Cabinet).where(or_(Cabinet.name == cabinet_model.name,
                                       Cabinet.number == cabinet_model.number))
    cabinet = await db.scalar(query)
    # if cabinet1 or cabinet2:
    if cabinet:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cabinet with given name or number already exists")

    cabinet = Cabinet(**cabinet_model.model_dump())
    db.add(cabinet)
    await db.commit()
    return cabinet

@app.get("/cabinets/", status_code=status.HTTP_200_OK, response_model=List[CabinetResponseModel])
async def get_cabinets(
    db: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0),
    limit: int = Query(10, gt=0)
    ):
    query = select(Cabinet).offset(offset).limit(limit)
    return await db.scalars(query)

if __name__ == "__main__":
    # asyncio.run(create_db())
    uvicorn.run("main:app")