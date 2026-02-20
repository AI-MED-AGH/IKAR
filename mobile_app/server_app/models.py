from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Devices(SQLModel, table=True):
    id: str = Field(primary_key=True)

    users: List["Users"] = Relationship(back_populates="device")

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str
    device_id: Optional[str] = Field(default=None, foreign_key="devices.id")

    device: Optional[Devices] = Relationship(back_populates="users")