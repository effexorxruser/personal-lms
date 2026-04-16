from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: str
    password_hash: str
    role: str = Field(default="learner")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
