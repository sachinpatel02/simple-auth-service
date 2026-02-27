from sqlmodel import SQLModel, Field, Relationship
import uuid
from pydantic import EmailStr
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id : uuid.UUID = Field(default_factory = uuid.uuid4, primary_key=True)
    email : EmailStr = Field(unique=True, index = True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool | None = Field(default=False)
    role: str | None = Field(default="user")
    created_at: datetime = Field(default = datetime.now(timezone.utc))
    updated_at: datetime = Field(default = datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")

class RefreshToken(SQLModel, table=True):
    id : uuid.UUID = Field(default_factory = uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    hashed_token: str
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    device_info: str | None = Field(default=None)

    user : User | None = Relationship(back_populates="refresh_tokens")
