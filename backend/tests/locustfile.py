import random
import string

from locust import HttpUser, between, task


def _rand_str(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class TaskManagerUser(HttpUser):
    """Имитирует зарегистрированного пользователя"""

    wait_time = between(0.3, 1.5)

    token: str | None = None
    task_ids: list[int]

    def on_start(self) -> None:
        self.task_ids = []
        username = f"load_{_rand_str()}"
        password = "LoadTest1234"

        self.client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        )

        r = self.client.post(
            "/api/auth/token",
            data={"username": username, "password": password},
            name="/api/auth/token (login)",
        )
        if r.status_code == 200:
            self.token = r.json().get("access_token")

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    # проверяем кэш

    @task(3)
    def list_tasks(self) -> None:
        self.client.get("/api/tasks", headers=self._headers, name="/api/tasks (list)")

    @task(2)
    def list_tasks_sorted(self) -> None:
        sort_by = random.choice(["title", "status", "created_at"])
        order = random.choice(["asc", "desc"])
        self.client.get(
            f"/api/tasks?sort_by={sort_by}&order={order}",
            headers=self._headers,
            name="/api/tasks?sort_by=... (list sorted)",
        )

    # инвалидирует кэш

    @task(2)
    def create_task(self) -> None:
        title = f"Task {_rand_str()}"
        priority = random.randint(0, 1000)
        r = self.client.post(
            "/api/tasks",
            json={"title": title, "priority": priority},
            headers=self._headers,
            name="/api/tasks (create)",
        )
        if r.status_code == 201:
            self.task_ids.append(r.json()["id"])

    @task(1)
    def get_task(self) -> None:
        if not self.task_ids:
            return
        task_id = random.choice(self.task_ids)
        self.client.get(
            f"/api/tasks/{task_id}",
            headers=self._headers,
            name="/api/tasks/{id} (get)",
        )

    @task(1)
    def search_tasks(self) -> None:
        query = random.choice(["task", "load", _rand_str(3), ""])
        self.client.get(
            f"/api/tasks/search?q={query}",
            headers=self._headers,
            name="/api/tasks/search",
        )

    @task(1)
    def top_priority(self) -> None:
        n = random.randint(1, 10)
        self.client.get(
            f"/api/tasks/top-priority?n={n}",
            headers=self._headers,
            name="/api/tasks/top-priority",
        )

    @task(1)
    def update_task(self) -> None:
        if not self.task_ids:
            return
        task_id = random.choice(self.task_ids)
        new_priority = random.randint(0, 1000)
        status = random.choice(["pending", "in_progress", "completed"])
        self.client.patch(
            f"/api/tasks/{task_id}",
            json={"priority": new_priority, "status": status},
            headers=self._headers,
            name="/api/tasks/{id} (update)",
        )

    @task(1)
    def delete_task(self) -> None:
        if not self.task_ids:
            return
        task_id = self.task_ids.pop(random.randrange(len(self.task_ids)))
        self.client.delete(
            f"/api/tasks/{task_id}",
            headers=self._headers,
            name="/api/tasks/{id} (delete)",
        )
