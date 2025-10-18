import asyncio
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from models import create_db, get_db


if __name__ == "__main__":
    asyncio.run(create_db())