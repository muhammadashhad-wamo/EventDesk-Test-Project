from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings

from app.routes import auth, user, event, booking, review, notification, ws

from app.tasks.jobs import start_scheduled_jobs, stop_scheduled_jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    job_tasks = start_scheduled_jobs()
    yield
    await stop_scheduled_jobs(job_tasks)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(user.admin_router)
app.include_router(event.router)
app.include_router(event.admin_router)
app.include_router(booking.router)
app.include_router(booking.admin_router)
app.include_router(review.router)
app.include_router(notification.router)
app.include_router(ws.router)