from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Association(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="users.username", primary_key=True)
    device_id: Optional[str] = Field(default=None, foreign_key="devices.id", primary_key=True)

class Devices(SQLModel, table=True):
    id: str = Field(primary_key=True)
    users: List["Users"] = Relationship(back_populates="devices", link_model=Association)

class Users(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password_hash: str

    devices: List[Devices] = Relationship(back_populates="users", link_model=Association)