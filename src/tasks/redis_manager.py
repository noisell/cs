from typing import Awaitable, Any
from redis import Redis

class RedisTaskManager:
    def __init__(self, host='redis_app', port=6380, db=0):
        self.r = Redis(host=host, port=port, db=db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.r.close()

    def add(self, name: str, mapping: dict) -> None:
        self.r.hmset(name, mapping)

    def add_one(self, name: str, key: str, value: Any) -> None:
        self.r.hset(name, key, value)

    def delete(self, *names: bytes | str | memoryview) -> None:
        self.r.delete(*names)

    def get(self, name: str) ->  Awaitable[dict] | dict:
        return self.r.hgetall(name)

    def keys(self, pattern: bytes | str | memoryview = "*", **kwargs: Any) -> Awaitable:
        return self.r.keys(pattern, **kwargs)

    def get_count(self, project_id: int) -> int:
        count = self.r.get(str(project_id))
        if not count:
            self.r.set(str(project_id), 0)
            return 0
        return int(count)

    def add_count(self, project_id: int) -> None:
        self.r.set(str(project_id), self.get_count(project_id) + 1)


task_manager = RedisTaskManager()