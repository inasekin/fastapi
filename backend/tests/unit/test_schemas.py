from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas import (
    STATUS_LABEL_RU,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
    Token,
    TokenPayload,
    UserCreate,
    UserPublic,
)

def test_task_status_pending_value():
    assert TaskStatus.pending == "pending"


def test_task_status_in_progress_value():
    assert TaskStatus.in_progress == "in_progress"


def test_task_status_completed_value():
    assert TaskStatus.completed == "completed"


def test_status_label_ru_pending():
    assert STATUS_LABEL_RU[TaskStatus.pending] == "в ожидании"


def test_status_label_ru_in_progress():
    assert STATUS_LABEL_RU[TaskStatus.in_progress] == "в работе"


def test_status_label_ru_completed():
    assert STATUS_LABEL_RU[TaskStatus.completed] == "завершено"


def test_status_label_ru_covers_all_statuses():
    for status in TaskStatus:
        assert status in STATUS_LABEL_RU

def test_user_create_valid():
    u = UserCreate(username="alice", password="pass1234")
    assert u.username == "alice"
    assert u.password == "pass1234"


def test_user_create_username_empty_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="", password="pass1234")


def test_user_create_username_too_long_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="a" * 65, password="pass1234")


def test_user_create_username_max_valid():
    u = UserCreate(username="a" * 64, password="pass1234")
    assert len(u.username) == 64


def test_user_create_password_too_short_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="abc")


def test_user_create_password_min_valid():
    u = UserCreate(username="alice", password="abcd")
    assert len(u.password) == 4


def test_user_create_password_too_long_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="a" * 129)

def test_task_create_defaults():
    t = TaskCreate(title="My Task")
    assert t.description == ""
    assert t.status == TaskStatus.pending
    assert t.priority == 0


def test_task_create_title_empty_raises():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_create_title_too_long_raises():
    with pytest.raises(ValidationError):
        TaskCreate(title="a" * 501)


def test_task_create_title_max_valid():
    t = TaskCreate(title="a" * 500)
    assert len(t.title) == 500


def test_task_create_priority_negative_raises():
    with pytest.raises(ValidationError):
        TaskCreate(title="T", priority=-1)


def test_task_create_priority_over_limit_raises():
    with pytest.raises(ValidationError):
        TaskCreate(title="T", priority=1001)


def test_task_create_priority_boundaries_valid():
    t0 = TaskCreate(title="T", priority=0)
    assert t0.priority == 0
    t1000 = TaskCreate(title="T", priority=1000)
    assert t1000.priority == 1000


def test_task_create_with_all_fields():
    t = TaskCreate(title="Full", description="desc", status=TaskStatus.in_progress, priority=50)
    assert t.description == "desc"
    assert t.status == TaskStatus.in_progress
    assert t.priority == 50

def test_task_update_all_fields_optional():
    u = TaskUpdate()
    assert u.title is None
    assert u.description is None
    assert u.status is None
    assert u.priority is None


def test_task_update_partial():
    u = TaskUpdate(title="New Title")
    assert u.title == "New Title"
    assert u.status is None


def test_task_update_invalid_title_raises():
    with pytest.raises(ValidationError):
        TaskUpdate(title="")


def test_task_update_priority_negative_raises():
    with pytest.raises(ValidationError):
        TaskUpdate(priority=-1)


def test_task_update_model_dump_exclude_unset():
    u = TaskUpdate(title="Only Title")
    data = u.model_dump(exclude_unset=True)
    assert "title" in data
    assert "status" not in data

def _make_orm_task(
    status="pending", id=1, user_id=1, title="T", description="", priority=0,
    created_at=None
):
    task = MagicMock()
    task.id = id
    task.user_id = user_id
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.created_at = created_at or datetime(2024, 1, 1, 12, 0, 0)
    return task


def test_from_orm_task_valid_status_preserved():
    task = _make_orm_task(status="in_progress")
    result = TaskRead.from_orm_task(task)
    assert result.status == TaskStatus.in_progress


def test_from_orm_task_completed_status():
    task = _make_orm_task(status="completed")
    result = TaskRead.from_orm_task(task)
    assert result.status == TaskStatus.completed
    assert result.status_label_ru == "завершено"


def test_from_orm_task_invalid_status_falls_back_to_pending():
    task = _make_orm_task(status="totally_invalid")
    result = TaskRead.from_orm_task(task)
    assert result.status == TaskStatus.pending


def test_from_orm_task_invalid_status_label_is_pending_label():
    task = _make_orm_task(status="bogus_status")
    result = TaskRead.from_orm_task(task)
    assert result.status_label_ru == "в ожидании"


def test_from_orm_task_fields_mapped_correctly():
    task = _make_orm_task(id=5, user_id=3, title="My Task", description="Desc", priority=100)
    result = TaskRead.from_orm_task(task)
    assert result.id == 5
    assert result.user_id == 3
    assert result.title == "My Task"
    assert result.description == "Desc"
    assert result.priority == 100


def test_from_orm_task_none_description_becomes_empty():
    task = _make_orm_task(description=None)
    result = TaskRead.from_orm_task(task)
    assert result.description == ""


def test_from_orm_task_status_label_pending():
    task = _make_orm_task(status="pending")
    result = TaskRead.from_orm_task(task)
    assert result.status_label_ru == "в ожидании"


def test_from_orm_task_status_label_in_progress():
    task = _make_orm_task(status="in_progress")
    result = TaskRead.from_orm_task(task)
    assert result.status_label_ru == "в работе"


def test_token_type_default():
    t = Token(access_token="abc123")
    assert t.token_type == "bearer"


def test_token_access_token_stored():
    t = Token(access_token="mytoken")
    assert t.access_token == "mytoken"


def test_token_payload_sub_none_default():
    p = TokenPayload()
    assert p.sub is None


def test_token_payload_sub_set():
    p = TokenPayload(sub="42")
    assert p.sub == "42"

def test_user_public_from_attributes():
    mock_user = MagicMock()
    mock_user.id = 7
    mock_user.username = "bob"
    u = UserPublic.model_validate(mock_user)
    assert u.id == 7
    assert u.username == "bob"
