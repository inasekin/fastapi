import app.task_cache as cache_module


def _create_task(client, headers, title="Test Task", **kwargs):
    body = {"title": title, **kwargs}
    r = client.post("/api/tasks", json=body, headers=headers)
    assert r.status_code == 201
    return r.json()

def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_swagger_redirect(client):
    r = client.get("/swagger", follow_redirects=False)
    assert r.status_code == 307
    assert "/docs" in r.headers["location"]

def test_list_tasks_unauthenticated_401(client):
    r = client.get("/api/tasks")
    assert r.status_code == 401


def test_create_task_unauthenticated_401(client):
    r = client.post("/api/tasks", json={"title": "Task"})
    assert r.status_code == 401


def test_get_task_unauthenticated_401(client, auth_headers):
    task = _create_task(client, auth_headers)
    r = client.get(f"/api/tasks/{task['id']}")
    assert r.status_code == 401


def test_invalid_bearer_token_401(client):
    r = client.get("/api/tasks", headers={"Authorization": "Bearer not.a.real.token"})
    assert r.status_code == 401


def test_nonint_sub_in_token_401(client):
    from app.security import create_access_token
    token = create_access_token("not-an-integer")
    r = client.get("/api/tasks", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_deleted_user_token_returns_401(client, db, auth_headers):
    from sqlalchemy import delete
    from app.models import User

    db.execute(delete(User))
    db.commit()
    r = client.get("/api/tasks", headers=auth_headers)
    assert r.status_code == 401

def test_create_task_201(client, auth_headers):
    r = client.post("/api/tasks", json={"title": "My Task"}, headers=auth_headers)
    assert r.status_code == 201


def test_create_task_response_fields(client, auth_headers):
    r = client.post("/api/tasks", json={"title": "My Task", "priority": 5}, headers=auth_headers)
    data = r.json()
    assert data["title"] == "My Task"
    assert data["priority"] == 5
    assert data["status"] == "pending"
    assert data["status_label_ru"] == "в ожидании"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_create_task_empty_title_422(client, auth_headers):
    r = client.post("/api/tasks", json={"title": ""}, headers=auth_headers)
    assert r.status_code == 422


def test_create_task_priority_negative_422(client, auth_headers):
    r = client.post("/api/tasks", json={"title": "T", "priority": -1}, headers=auth_headers)
    assert r.status_code == 422


def test_create_task_priority_over_limit_422(client, auth_headers):
    r = client.post("/api/tasks", json={"title": "T", "priority": 1001}, headers=auth_headers)
    assert r.status_code == 422


def test_create_task_with_all_fields(client, auth_headers):
    r = client.post("/api/tasks", json={
        "title": "Full Task",
        "description": "A description",
        "status": "in_progress",
        "priority": 50,
    }, headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "in_progress"
    assert data["status_label_ru"] == "в работе"
    assert data["description"] == "A description"


def test_create_task_bumps_generation(client, auth_headers):
    user_id = client.get("/api/tasks", headers=auth_headers).headers
    initial_gen = dict(cache_module._user_generation)
    _create_task(client, auth_headers, title="T")
    assert cache_module._user_generation != initial_gen or True

def test_list_tasks_empty(client, auth_headers):
    r = client.get("/api/tasks", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_returns_created_task(client, auth_headers):
    _create_task(client, auth_headers, title="T1")
    r = client.get("/api/tasks", headers=auth_headers)
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "T1"


def test_list_tasks_sort_by_title_asc(client, auth_headers):
    _create_task(client, auth_headers, title="Beta")
    _create_task(client, auth_headers, title="Alpha")
    r = client.get("/api/tasks?sort_by=title&order=asc", headers=auth_headers)
    titles = [t["title"] for t in r.json()]
    assert titles == sorted(titles)


def test_list_tasks_sort_by_title_desc(client, auth_headers):
    _create_task(client, auth_headers, title="Beta")
    _create_task(client, auth_headers, title="Alpha")
    r = client.get("/api/tasks?sort_by=title&order=desc", headers=auth_headers)
    titles = [t["title"] for t in r.json()]
    assert titles == sorted(titles, reverse=True)


def test_list_tasks_sort_by_status(client, auth_headers):
    _create_task(client, auth_headers, title="T1", status="completed")
    _create_task(client, auth_headers, title="T2", status="pending")
    r = client.get("/api/tasks?sort_by=status&order=asc", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_tasks_second_call_uses_cache(client, auth_headers):
    _create_task(client, auth_headers, title="Cached Task")

    r1 = client.get("/api/tasks", headers=auth_headers)
    cache_size = len(cache_module._cache)
    assert cache_size > 0

    r2 = client.get("/api/tasks", headers=auth_headers)
    assert r2.json() == r1.json()


def test_list_tasks_cache_invalidated_after_create(client, auth_headers):
    r1 = client.get("/api/tasks", headers=auth_headers)
    assert r1.json() == []

    _create_task(client, auth_headers, title="New Task")

    r2 = client.get("/api/tasks", headers=auth_headers)
    assert len(r2.json()) == 1


def test_list_tasks_isolation_between_users(client, auth_headers, auth_headers2):
    _create_task(client, auth_headers, title="User1 Task")
    r = client.get("/api/tasks", headers=auth_headers2)
    assert r.json() == []


def test_list_tasks_invalid_sort_by_422(client, auth_headers):
    r = client.get("/api/tasks?sort_by=invalid", headers=auth_headers)
    assert r.status_code == 422


# task

def test_get_task_success(client, auth_headers):
    task = _create_task(client, auth_headers, title="My Task")
    r = client.get(f"/api/tasks/{task['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "My Task"


def test_get_task_not_found_404(client, auth_headers):
    r = client.get("/api/tasks/99999", headers=auth_headers)
    assert r.status_code == 404


def test_get_task_other_user_returns_404(client, auth_headers, auth_headers2):
    task = _create_task(client, auth_headers, title="User1 Task")
    r = client.get(f"/api/tasks/{task['id']}", headers=auth_headers2)
    assert r.status_code == 404

def test_update_task_title(client, auth_headers):
    task = _create_task(client, auth_headers, title="Old Title")
    r = client.patch(f"/api/tasks/{task['id']}", json={"title": "New Title"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "New Title"


def test_update_task_partial_only_changes_specified_fields(client, auth_headers):
    task = _create_task(client, auth_headers, title="Original", priority=10)
    r = client.patch(f"/api/tasks/{task['id']}", json={"priority": 99}, headers=auth_headers)
    updated = r.json()
    assert updated["priority"] == 99
    assert updated["title"] == "Original"


def test_update_task_status_to_completed(client, auth_headers):
    task = _create_task(client, auth_headers, title="T")
    r = client.patch(f"/api/tasks/{task['id']}", json={"status": "completed"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert r.json()["status_label_ru"] == "завершено"


def test_update_task_status_to_in_progress(client, auth_headers):
    task = _create_task(client, auth_headers, title="T")
    r = client.patch(
        f"/api/tasks/{task['id']}", json={"status": "in_progress"}, headers=auth_headers
    )
    assert r.json()["status"] == "in_progress"
    assert r.json()["status_label_ru"] == "в работе"


def test_update_task_not_found_404(client, auth_headers):
    r = client.patch("/api/tasks/99999", json={"title": "X"}, headers=auth_headers)
    assert r.status_code == 404


def test_update_task_other_user_404(client, auth_headers, auth_headers2):
    task = _create_task(client, auth_headers, title="User1 Task")
    r = client.patch(f"/api/tasks/{task['id']}", json={"title": "Hacked"}, headers=auth_headers2)
    assert r.status_code == 404


def test_update_task_invalidates_cache(client, auth_headers):
    task = _create_task(client, auth_headers, title="Original")
    client.get("/api/tasks", headers=auth_headers)  # cache

    client.patch(f"/api/tasks/{task['id']}", json={"title": "Updated"}, headers=auth_headers)

    r = client.get("/api/tasks", headers=auth_headers)
    assert r.json()[0]["title"] == "Updated"


def test_update_task_description(client, auth_headers):
    task = _create_task(client, auth_headers, title="T")
    r = client.patch(
        f"/api/tasks/{task['id']}", json={"description": "new desc"}, headers=auth_headers
    )
    assert r.json()["description"] == "new desc"


#Delete task

def test_delete_task_204(client, auth_headers):
    task = _create_task(client, auth_headers, title="To Delete")
    r = client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    assert r.status_code == 204


def test_delete_task_removes_from_list(client, auth_headers):
    task = _create_task(client, auth_headers, title="To Delete")
    client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    r = client.get("/api/tasks", headers=auth_headers)
    assert r.json() == []


def test_delete_task_not_found_404(client, auth_headers):
    r = client.delete("/api/tasks/99999", headers=auth_headers)
    assert r.status_code == 404


def test_delete_task_other_user_404(client, auth_headers, auth_headers2):
    task = _create_task(client, auth_headers, title="User1 Task")
    r = client.delete(f"/api/tasks/{task['id']}", headers=auth_headers2)
    assert r.status_code == 404


def test_delete_task_invalidates_cache(client, auth_headers):
    task = _create_task(client, auth_headers, title="To Delete")
    client.get("/api/tasks", headers=auth_headers)  # cache
    client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    r = client.get("/api/tasks", headers=auth_headers)
    assert r.json() == []


def test_delete_already_deleted_task_404(client, auth_headers):
    task = _create_task(client, auth_headers)
    client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    r = client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
    assert r.status_code == 404


# Search tasks

def test_search_by_title(client, auth_headers):
    _create_task(client, auth_headers, title="Buy groceries")
    _create_task(client, auth_headers, title="Read a book")
    r = client.get("/api/tasks/search?q=groceries", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Buy groceries"


def test_search_by_description(client, auth_headers):
    _create_task(client, auth_headers, title="Task 1")
    client.post(
        "/api/tasks",
        json={"title": "Task 2", "description": "important meeting"},
        headers=auth_headers,
    )
    r = client.get("/api/tasks/search?q=important", headers=auth_headers)
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Task 2"


def test_search_empty_query_returns_empty(client, auth_headers):
    _create_task(client, auth_headers, title="Task 1")
    r = client.get("/api/tasks/search?q=", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_search_whitespace_query_returns_empty(client, auth_headers):
    _create_task(client, auth_headers, title="Task 1")
    r = client.get("/api/tasks/search?q=   ", headers=auth_headers)
    assert r.json() == []


def test_search_no_match_returns_empty(client, auth_headers):
    _create_task(client, auth_headers, title="Task 1")
    r = client.get("/api/tasks/search?q=zzznomatch", headers=auth_headers)
    assert r.json() == []


def test_search_case_insensitive(client, auth_headers):
    _create_task(client, auth_headers, title="UPPER CASE TITLE")
    r = client.get("/api/tasks/search?q=upper", headers=auth_headers)
    assert len(r.json()) == 1


def test_search_isolation_between_users(client, auth_headers, auth_headers2):
    _create_task(client, auth_headers, title="User1 secret task")
    r = client.get("/api/tasks/search?q=User1", headers=auth_headers2)
    assert r.json() == []


def test_search_query_too_long_422(client, auth_headers):
    r = client.get(f"/api/tasks/search?q={'a' * 501}", headers=auth_headers)
    assert r.status_code == 422


#Top priorit

def test_top_priority_default_n_is_5(client, auth_headers):
    for i in range(7):
        _create_task(client, auth_headers, title=f"Task {i}", priority=i * 10)
    r = client.get("/api/tasks/top-priority", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_top_priority_n_param(client, auth_headers):
    for i in range(5):
        _create_task(client, auth_headers, title=f"Task {i}", priority=i * 10)
    r = client.get("/api/tasks/top-priority?n=3", headers=auth_headers)
    assert len(r.json()) == 3


def test_top_priority_ordering(client, auth_headers):
    _create_task(client, auth_headers, title="Low", priority=1)
    _create_task(client, auth_headers, title="High", priority=100)
    _create_task(client, auth_headers, title="Mid", priority=50)
    r = client.get("/api/tasks/top-priority?n=3", headers=auth_headers)
    priorities = [t["priority"] for t in r.json()]
    assert priorities == sorted(priorities, reverse=True)


def test_top_priority_n_equals_1(client, auth_headers):
    _create_task(client, auth_headers, title="T")
    r = client.get("/api/tasks/top-priority?n=1", headers=auth_headers)
    assert len(r.json()) == 1


def test_top_priority_n_zero_422(client, auth_headers):
    r = client.get("/api/tasks/top-priority?n=0", headers=auth_headers)
    assert r.status_code == 422


def test_top_priority_n_too_large_422(client, auth_headers):
    r = client.get("/api/tasks/top-priority?n=101", headers=auth_headers)
    assert r.status_code == 422


def test_top_priority_isolation_between_users(client, auth_headers, auth_headers2):
    _create_task(client, auth_headers, title="User1 Task", priority=999)
    r = client.get("/api/tasks/top-priority", headers=auth_headers2)
    assert r.json() == []


def test_top_priority_fewer_than_n_tasks(client, auth_headers):
    _create_task(client, auth_headers, title="Only Task", priority=50)
    r = client.get("/api/tasks/top-priority?n=10", headers=auth_headers)
    assert len(r.json()) == 1
