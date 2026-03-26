from threading import Lock

from cachetools import TTLCache

from app.config import settings

_cache: TTLCache[tuple, list[dict]] = TTLCache(maxsize=512, ttl=settings.list_cache_ttl_seconds)
_lock = Lock()
_user_generation: dict[int, int] = {}


def bump_user_generation(user_id: int) -> None:
    with _lock:
        _user_generation[user_id] = _user_generation.get(user_id, 0) + 1


def _generation(user_id: int) -> int:
    with _lock:
        return _user_generation.get(user_id, 0)


def list_cache_get(user_id: int, sort_by: str, order: str) -> list[dict] | None:
    key = (user_id, _generation(user_id), sort_by, order)
    with _lock:
        raw = _cache.get(key)
        return list(raw) if raw is not None else None


def list_cache_set(user_id: int, sort_by: str, order: str, value: list) -> None:
    key = (user_id, _generation(user_id), sort_by, order)
    with _lock:
        _cache[key] = [t.model_dump(mode="json") for t in value]
