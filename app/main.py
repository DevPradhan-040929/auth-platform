from fastapi import FastAPI
from app.database import Base, engine
from app.api import users
from app.models import user  
from app.api import admin, user_routes

app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(users.router)

app.include_router(admin.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"status": "ok"}
