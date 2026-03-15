from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_minutes: int

    def has_enough_time(self, minutes: int) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str
    task_type: str

    def priority_rank(self) -> int:
        pass


@dataclass
class ScheduledEntry:
    task: CareTask
    start_time: str
    reasoning: str


@dataclass
class DailySchedule:
    entries: list[ScheduledEntry] = field(default_factory=list)
    summary: str = ""

    def to_dict_list(self) -> list[dict]:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[CareTask]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate(self) -> DailySchedule:
        pass

    def _assign_start_times(self, entries: list[CareTask]) -> list[ScheduledEntry]:
        pass
