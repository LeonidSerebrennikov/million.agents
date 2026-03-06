from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.core.db import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    owned_projects = relationship("Project", back_populates="owner")
    executor_tasks = relationship("Task", foreign_keys="Task.executor_id", back_populates="executor")
    authored_tasks = relationship("Task", foreign_keys="Task.author_id", back_populates="author")
    status_changes = relationship("TaskLog", back_populates="changed_by_user")