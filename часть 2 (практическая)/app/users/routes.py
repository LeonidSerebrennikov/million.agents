from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.users import service, schemas

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.User)
async def create_user(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        project = await service.create_user(db, user_data)
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    