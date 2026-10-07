from fastapi import FastAPI

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.user import user_router
from app.routes.user import admin_router as user_router_admin
from app.routes.event import router as event_router
from app.routes.event import admin_router as event_router_admin


app = FastAPI(title=settings.APP_NAME)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(user_router_admin)
app.include_router(event_router)
app.include_router(event_router_admin)