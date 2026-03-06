from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class ProjectCreate(ProjectBase):
    owner_id: int

class ProjectBrief(BaseModel):
    id: int
    title: str
    
    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectMemberBase(BaseModel):
    user_id: int
    project_id: int

class ProjectMember(ProjectMemberBase):
    joined_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
