from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.projects import service, schemas

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.Project)
async def create_project(project_data: schemas.ProjectCreate, db: AsyncSession = Depends(get_db)):
    try:
        project = await service.create_project(db, project_data)
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
