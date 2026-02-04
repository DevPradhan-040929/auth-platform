from fastapi import FastAPI
from app.database import Base, engine
from app.api import users
from app.models import user  
app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "ok"}
