from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.tasks import service, schemas, models

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.Task)
async def create_task(
    task_data: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        task = await service.create_task(db, task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/", response_model=List[schemas.Task])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    executor_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    sort_by: str = Query("created_at", regex="created_at|priority"),
    sort_order: str = Query("desc", regex="asc|desc")
):
    status_enum = None
    if status:
        try:
            status_enum = models.TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    priority_enum = None
    if priority:
        try:
            priority_enum = models.TaskPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    
    tasks = await service.get_tasks(
        db,
        skip=skip,
        limit=limit,
        status=status_enum,
        priority=priority_enum,
        executor_id=executor_id,
        project_id=project_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return tasks


@router.get("/{task_id}", response_model=schemas.Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await service.get_task_with_relations(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=schemas.Task)
async def update_task_status(
    task_id: int,
    status_update: schemas.TaskStatusUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        task = await service.update_task_status(
            db,
            task_id,
            status_update.new_status,
            user_id
        )
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/{task_id}/history", response_model=list[schemas.TaskLog])
async def get_task_history(task_id: int, db: AsyncSession = Depends(get_db)):
    try:
        task_logs = await service.get_task_history(db, task_id)
        return task_logs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))