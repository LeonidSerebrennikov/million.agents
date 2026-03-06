from typing import Optional, List, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, asc, desc, exists
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.tasks import models, schemas
from app.users import service as user_service
from app.projects import service as project_service


STATUS_TRANSITIONS = {
    models.TaskStatus.CREATED: [
        models.TaskStatus.IN_PROGRESS,
        models.TaskStatus.CANCELLED
    ],
    models.TaskStatus.IN_PROGRESS: [
        models.TaskStatus.REVIEW,
        models.TaskStatus.CREATED
    ],
    models.TaskStatus.REVIEW: [
        models.TaskStatus.DONE,
        models.TaskStatus.IN_PROGRESS
    ],
    models.TaskStatus.DONE: [],
    models.TaskStatus.CANCELLED: []
}

PRIORITY_ORDER = {
    models.TaskPriority.LOW: 1,
    models.TaskPriority.MEDIUM: 2,
    models.TaskPriority.HIGH: 3,
    models.TaskPriority.CRITICAL: 4
}

async def create_task(db: AsyncSession, task_data: schemas.TaskCreate) -> models.Task:
    project = await project_service.get_project(db, task_data.project_id)
    if not project:
        raise ValueError(f"Project with id {task_data.project_id} not found")
    
    author = await user_service.get_user(db, task_data.author_id)
    if not author:
        raise ValueError(f"Author with id {task_data.author_id} not found")
    
    if task_data.executor_id == 0:
        task_data.executor_id = None

    if task_data.executor_id:
        executor = await user_service.get_user(db, task_data.executor_id)
        if not executor:
            raise ValueError(f"Executor with id {task_data.executor_id} not found")
    
    task = models.Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        project_id=task_data.project_id,
        author_id=task_data.author_id,
        executor_id=task_data.executor_id,
        status=models.TaskStatus.CREATED 
    )
    
    db.add(task)
    await db.commit()

    result = await db.execute(
        select(models.Task)
        .where(models.Task.id == task.id)
        .options(
            selectinload(models.Task.author),
            selectinload(models.Task.executor)
        )
    )
    task = result.scalar_one()
    
    return task


async def get_task(db: AsyncSession, task_id: int) -> Optional[models.Task]:
    task = await db.get(models.Task, task_id)
    return task


async def exist_task(db: AsyncSession, task_id: int) -> bool:
    stmt = select(exists().where(models.Task.id == task_id))
    result = await db.execute(stmt)
    return bool(result.scalar())

async def get_task_with_relations(db: AsyncSession, task_id: int) -> Optional[models.Task]:

    query = select(models.Task).where(
        models.Task.id == task_id
    ).options(
        selectinload(models.Task.author),
        selectinload(models.Task.executor),
        selectinload(models.Task.project),
        selectinload(models.Task.status_history).selectinload(models.TaskLog.changed_by_user)
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TaskStatus] = None,
    priority: Optional[models.TaskPriority] = None,
    executor_id: Optional[int] = None,
    project_id: Optional[int] = None,
    author_id: Optional[int] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[models.Task]:

    query = select(models.Task).options(
        selectinload(models.Task.author),
        selectinload(models.Task.executor),
        selectinload(models.Task.project)
    )

    count_query = select(func.count()).select_from(models.Task)

    filters = []
    if status:
        filters.append(models.Task.status == status)
    if priority:
        filters.append(models.Task.priority == priority)
    if executor_id:
        filters.append(models.Task.executor_id == executor_id)
    if project_id:
        filters.append(models.Task.project_id == project_id)
    if author_id:
        filters.append(models.Task.author_id == author_id)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    match sort_by:
        case "priority":
            order_column = models.Task.priority
        case _:
            order_column = models.Task.created_at
            

    if sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tasks = list(result.unique().scalars().all())
    
    return tasks


async def delete_task(db: AsyncSession, task_id: int):
    pass


async def update_task_status(
    db: AsyncSession,
    task_id: int,
    new_status: models.TaskStatus,
    changed_by: int
) -> Optional[models.Task]:
    
    task = await get_task(db, task_id)
    if not task:
        return None
    
    user = await user_service.get_user(db, changed_by)
    if not user:
        raise ValueError(f"User with id {changed_by} not found")

    if not _is_transition_allowed(task.status, new_status):
        raise ValueError(f"Invalid status transition from {task.status.value} to {new_status.value}. ")

    if task.status == new_status:
        result = await db.execute(
        select(models.Task)
        .where(models.Task.id == task_id)
        .options(
            selectinload(models.Task.author),
            selectinload(models.Task.executor)
        )
    )
        return result.scalar_one_or_none()
    
    old_status = task.status
    task.status = new_status
    task.updated_at = datetime.now()
    
    log = models.TaskLog(
        task_id=task_id,
        changed_by=changed_by,
        from_status=old_status,
        to_status=new_status
    )
    db.add(log)
    
    await db.commit()
    
    result = await db.execute(
        select(models.Task)
        .where(models.Task.id == task_id)
        .options(
            selectinload(models.Task.author),
            selectinload(models.Task.executor)
        )
    )
    task = result.scalar_one()
    
    return task


def _is_transition_allowed(current: models.TaskStatus, new: models.TaskStatus) -> bool:
    if current == new:
        return True
    return new in STATUS_TRANSITIONS.get(current, [])


async def get_task_history(db: AsyncSession, task_id: int) -> List[models.TaskLog]:
    if not await exist_task(db, task_id):
        raise ValueError(f"Task with id {task_id} does not exist")

    result = await db.execute(
        select(models.TaskLog)
        .where(models.TaskLog.task_id == task_id)
        .order_by(desc(models.TaskLog.changed_at))
    )
    return list(result.scalars().all())
