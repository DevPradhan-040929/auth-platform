from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth Platform"
    SECRET_KEY: str = "change-this-later"

settings = Settings()
