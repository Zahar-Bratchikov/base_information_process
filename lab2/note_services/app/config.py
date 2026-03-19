from pydantic import BaseModel


class Settings(BaseModel):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    db_path: str = "./data/notes.db"


def load_settings() -> Settings:
    import os

    return Settings(
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
        redis_password=os.getenv("REDIS_PASSWORD") or None,
        db_path=os.getenv("DB_PATH", "./data/notes.db"),
    )

