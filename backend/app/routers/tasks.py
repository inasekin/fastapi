from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Task, User
from app.schemas import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.task_cache import bump_user_generation, list_cache_get, list_cache_set

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_read_list(tasks: list[Task]) -> list[TaskRead]:
    return [TaskRead.from_orm_task(t) for t in tasks]


@router.get("", response_model=list[TaskRead])
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    sort_by: Literal["title", "status", "created_at"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> list[TaskRead]:
    cached = list_cache_get(current_user.id, sort_by, order)
    if cached is not None:
        return [TaskRead.model_validate(row) for row in cached]

    column = getattr(Task, sort_by)
    stmt = select(Task).where(Task.user_id == current_user.id)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    rows = list(db.scalars(stmt).all())
    out = _task_read_list(rows)
    list_cache_set(current_user.id, sort_by, order, out)
    return out


@router.get("/search", response_model=list[TaskRead])
def search_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: str = Query("", min_length=0, max_length=500),
) -> list[TaskRead]:
    if not q.strip():
        return []
    all_rows = list(db.scalars(select(Task).where(Task.user_id == current_user.id)).all())
    needle = q.lower()
    matched: list[Task] = []
    for t in all_rows:
        title = (t.title or "").lower()
        desc = (t.description or "").lower()
        if needle in title or needle in desc:
            matched.append(t)
    return _task_read_list(matched)


@router.get("/top-priority", response_model=list[TaskRead])
def top_by_priority(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    n: int = Query(5, ge=1, le=100, description="Сколько самых приоритетных задач вернуть"),
) -> list[TaskRead]:
    stmt = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.priority.desc(), Task.created_at.desc())
        .limit(n)
    )
    rows = list(db.scalars(stmt).all())
    return _task_read_list(rows)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TaskRead:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return TaskRead.from_orm_task(task)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TaskRead:
    task = Task(
        user_id=current_user.id,
        title=body.title,
        description=body.description or "",
        status=body.status.value,
        priority=body.priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    bump_user_generation(current_user.id)
    return TaskRead.from_orm_task(task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TaskRead:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    data = body.model_dump(exclude_unset=True)
    if "status" in data and isinstance(data["status"], TaskStatus):
        data["status"] = data["status"].value
    for key, value in data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    bump_user_generation(current_user.id)
    return TaskRead.from_orm_task(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    db.delete(task)
    db.commit()
    bump_user_generation(current_user.id)
