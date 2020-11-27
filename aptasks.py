import asyncio
import jsons
from jsons import JsonSerializable
from datetime import datetime
from typing import Dict, Union


class APTask(JsonSerializable):
    def __init__(
        self,
        uid: int,
        count: int,
        delta: float,
        start: float,
        interval: float,
        date_start=None,
    ):
        self.count = count
        self.delta = delta
        self.start = start
        self.interval = interval
        self.uid = uid
        self.value = start
        self.status = "SHEDULED"

    def __str__(self):
        text = (
            f"task {self.uid}: {self.status}, start={self.start},d={self.delta}, "
            f"i={self.interval} current_value={self.value}"
        )
        return text

    def calc(self):
        self.value += self.delta


class APTaskManager:
    def __init__(self, q: asyncio.Queue, tasks: Dict[int, APTask]):
        self.q = q
        self.task_counter: int = 0
        self.tasks = tasks

    async def addtask(
        self, count: int, delta: float, start: float, interval: float
    ) -> int:
        self.task_counter += 1
        uid = self.task_counter
        self.tasks[uid] = APTask(uid, count, delta, start, interval)
        await self.q.put(uid)
        return uid

    def taskdone(self, task_id) -> None:
        del self.tasks[task_id]
        self.q.task_done()
