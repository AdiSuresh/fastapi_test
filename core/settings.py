from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'FastAPI Test'
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 10
    DATABASE_URL: str = "postgresql://postgres:qwertyuiop@localhost:5000/fastapi_test"

    class Config:
        env_file = '.env'

settings = Settings()