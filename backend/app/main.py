from fastapi import FastAPI

from app.core.config import settings

from app.routes import auth, user, event, booking, review


app = FastAPI(title=settings.APP_NAME)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(user.admin_router)
app.include_router(event.router)
app.include_router(event.admin_router)
app.include_router(booking.router)
app.include_router(booking.admin_router)
app.include_router(review.router)