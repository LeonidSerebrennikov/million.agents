from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )

class UserBrief(BaseModel):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )