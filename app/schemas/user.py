from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
