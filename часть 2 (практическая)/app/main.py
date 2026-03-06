from fastapi import FastAPI
from app.core.config import settings
from app.users import routes as users_endpoints
from app.projects import routes as projects_endpoints
from app.tasks import routes as tasks_endpoints

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(users_endpoints.router)
app.include_router(projects_endpoints.router)
app.include_router(tasks_endpoints.router)