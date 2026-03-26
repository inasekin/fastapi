from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


STATUS_LABEL_RU = {
    TaskStatus.pending: "в ожидании",
    TaskStatus.in_progress: "в работе",
    TaskStatus.completed: "завершено",
}


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=4, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    status: TaskStatus = TaskStatus.pending
    priority: int = Field(default=0, ge=0, le=1000)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=1000)


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    status_label_ru: str

    @classmethod
    def from_orm_task(cls, task) -> "TaskRead":
        try:
            st = TaskStatus(task.status)
        except ValueError:
            st = TaskStatus.pending
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description or "",
            status=st,
            priority=task.priority,
            created_at=task.created_at,
            status_label_ru=STATUS_LABEL_RU.get(st, task.status),
        )
