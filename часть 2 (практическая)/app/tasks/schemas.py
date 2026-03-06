from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.tasks.models import TaskPriority, TaskStatus
from app.users.schemas import UserBrief

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    executor_id: Optional[int] = None

class TaskCreate(TaskBase):
    project_id: int
    author_id: int 

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    executor_id: Optional[int] = None

class TaskStatusUpdate(BaseModel):
    new_status: TaskStatus

class Task(TaskBase):
    id: int
    status: TaskStatus
    project_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    author: Optional[UserBrief] = None
    executor: Optional[UserBrief] = None
    
    model_config = ConfigDict(
        from_attributes=True
    )



class TaskLogBase(BaseModel):
    id: int
    changed_at: datetime


class TaskLog(TaskLogBase):
    task_id: int
    from_status: TaskStatus
    to_status: TaskStatus
    changed_by: int
    
    model_config = ConfigDict(
        from_attributes=True
    )
    