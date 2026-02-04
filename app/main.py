from fastapi import FastAPI

app = FastAPI(title="Auth Platform")

@app.get("/")
def root():
    return {"message": "Auth platform is running 🚀"}
