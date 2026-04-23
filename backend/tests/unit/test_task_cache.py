from datetime import datetime

import app.task_cache as cache_module
from app.schemas import STATUS_LABEL_RU, TaskRead, TaskStatus
from app.task_cache import bump_user_generation, list_cache_get, list_cache_set


def _make_task_read(id=1, user_id=1, title="Task", status=TaskStatus.pending, priority=0):
    return TaskRead(
        id=id,
        user_id=user_id,
        title=title,
        description="",
        status=status,
        priority=priority,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        status_label_ru=STATUS_LABEL_RU[status],
    )


def test_cache_miss_returns_none():
    result = list_cache_get(999, "created_at", "desc")
    assert result is None


def test_cache_set_then_get():
    task = _make_task_read()
    list_cache_set(1, "created_at", "desc", [task])
    result = list_cache_get(1, "created_at", "desc")
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_cache_stores_data_as_dicts():
    task = _make_task_read(title="My Task")
    list_cache_set(1, "title", "asc", [task])
    result = list_cache_get(1, "title", "asc")
    assert isinstance(result[0], dict)
    assert result[0]["title"] == "My Task"


def test_cache_returns_copy_not_same_reference():
    task = _make_task_read()
    list_cache_set(1, "created_at", "desc", [task])
    r1 = list_cache_get(1, "created_at", "desc")
    r2 = list_cache_get(1, "created_at", "desc")
    assert r1 is not r2


def test_bump_generation_invalidates_cache():
    task = _make_task_read()
    list_cache_set(1, "created_at", "desc", [task])
    assert list_cache_get(1, "created_at", "desc") is not None

    bump_user_generation(1)

    assert list_cache_get(1, "created_at", "desc") is None


def test_bump_generation_increments_counter():
    initial = cache_module._user_generation.get(42, 0)
    bump_user_generation(42)
    bump_user_generation(42)
    bump_user_generation(42)
    assert cache_module._user_generation[42] == initial + 3


def test_different_sort_params_are_independent():
    task = _make_task_read()
    list_cache_set(1, "created_at", "desc", [task])
    assert list_cache_get(1, "created_at", "desc") is not None
    assert list_cache_get(1, "title", "asc") is None


def test_different_users_have_independent_cache():
    task1 = _make_task_read(id=1, user_id=1)
    task2 = _make_task_read(id=2, user_id=2)
    list_cache_set(1, "created_at", "desc", [task1])
    list_cache_set(2, "created_at", "desc", [task2])

    bump_user_generation(1)

    assert list_cache_get(1, "created_at", "desc") is None
    result = list_cache_get(2, "created_at", "desc")
    assert result is not None
    assert result[0]["id"] == 2


def test_empty_list_cached():
    list_cache_set(1, "created_at", "desc", [])
    result = list_cache_get(1, "created_at", "desc")
    assert result == []


def test_multiple_tasks_cached():
    tasks = [_make_task_read(id=i) for i in range(1, 4)]
    list_cache_set(1, "created_at", "desc", tasks)
    result = list_cache_get(1, "created_at", "desc")
    assert len(result) == 3


def test_cache_serializes_datetime_to_json():
    task = _make_task_read()
    list_cache_set(1, "created_at", "desc", [task])
    result = list_cache_get(1, "created_at", "desc")
    # model_dump(mode="json") converts datetime to ISO string
    assert isinstance(result[0]["created_at"], str)
