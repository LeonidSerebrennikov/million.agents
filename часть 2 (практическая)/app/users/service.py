from app.users import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
    user = models.User()
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def get_user(db: AsyncSession, user_id: int) -> models.User | None:
    user = await db.get(models.User, user_id)
    return user


