from typing import Optional, List
from app.projects.schemas import ProjectCreate, Project, ProjectMember
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.users import service as s_user
from app.projects import models

async def create_project(db: AsyncSession, project_data: ProjectCreate) -> models.Project:
    owner = await s_user.get_user(db, project_data.owner_id)
    if not owner:
        raise ValueError(f"Owner with id {project_data.owner_id} not found")
    

    project = models.Project(title=project_data.title, description=project_data.description, owner_id=project_data.owner_id)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    await add_member(db, project.id, project_data.owner_id)

    return project

async def get_project(db: AsyncSession, project_id: int) -> models.Project | None:
    result = await db.get(models.Project, project_id)
    return result

async def remove_project(db: AsyncSession, project_id: int):
    pass

async def add_member(db: AsyncSession, project_id: int, user_id: int) -> models.ProjectMember:

    project = await get_project(db, project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found")
    
    user = await s_user.get_user(db, user_id)
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    existing = await get_member(db, project.id, user_id)
    
    if existing.scalar_one_or_none():
        raise ValueError(f"User {user_id} is already a member")
    
    member = models.ProjectMember(
        project_id=project_id,
        user_id=user_id
    )
    
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return member

async def remove_member(db: AsyncSession, project_id: int, user_id: int):
    pass

async def get_member(db: AsyncSession, project_id: int, user_id: int):
    return await db.execute(select(models.ProjectMember).where(and_(models.ProjectMember.project_id == project_id,models.ProjectMember.user_id == user_id)))