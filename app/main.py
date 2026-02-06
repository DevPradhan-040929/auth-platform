from fastapi import FastAPI
from app.database import Base, engine
from app.api import users
from app.models import user  
from app.api import admin, user_routes
from app.api import auth
from app.api import dashboard
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

app.include_router(admin.router)
app.include_router(user_routes.router)
app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok"}

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Slow down."},
    )
