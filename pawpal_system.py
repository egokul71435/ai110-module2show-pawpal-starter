from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
from typing import Literal

FREQUENCY_DELTAS: dict[str, timedelta] = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


@dataclass
class CareTask:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    task_type: str
    frequency: str = "daily"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def priority_rank(self) -> int:
        """Return a numeric score for sorting: high=3, medium=2, low=1."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def mark_complete(self) -> CareTask | None:
        """Mark this task as completed; return next occurrence if recurring."""
        self.completed = True
        delta = FREQUENCY_DELTAS.get(self.frequency)
        if delta is None:
            return None
        return CareTask(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            task_type=self.task_type,
            frequency=self.frequency,
            due_date=self.due_date + delta,
        )

    def reset(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False


@dataclass
class Pet:
    """Stores pet details and holds a list of care tasks."""

    name: str
    species: str
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task matching the given title; return True if found."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def complete_task(self, title: str) -> CareTask | None:
        """Mark a task done and auto-add its next occurrence if recurring."""
        for task in self.tasks:
            if task.title == title and not task.completed:
                next_task = task.mark_complete()
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        return None

    def get_pending_tasks(self) -> list[CareTask]:
        """Return all tasks that have not been marked complete."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[CareTask]:
        """Return every task across all pets."""
        tasks: list[CareTask] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def get_all_pending_tasks(self) -> list[CareTask]:
        """Return only incomplete tasks across all pets."""
        pending: list[CareTask] = []
        for pet in self.pets:
            pending.extend(pet.get_pending_tasks())
        return pending

    def has_enough_time(self, minutes: int) -> bool:
        """Check whether the given duration fits within available_minutes."""
        return minutes <= self.available_minutes


@dataclass
class ScheduledEntry:
    """One row in the daily plan: a task paired with a start time and reasoning."""

    task: CareTask
    start_time: str
    reasoning: str


@dataclass
class DailySchedule:
    """The output artifact: an ordered list of scheduled entries plus a summary."""

    entries: list[ScheduledEntry] = field(default_factory=list)
    summary: str = ""

    def sort_by_time(self) -> DailySchedule:
        """Return a new DailySchedule with entries sorted by start_time (HH:MM)."""
        sorted_entries = sorted(
            self.entries,
            key=lambda e: tuple(int(p) for p in e.start_time.split(":")),
        )
        return DailySchedule(entries=sorted_entries, summary=self.summary)

    def to_dict_list(self) -> list[dict]:
        """Convert entries to a list of plain dicts for st.table()."""
        return [
            {
                "time": entry.start_time,
                "task": entry.task.title,
                "duration": entry.task.duration_minutes,
                "priority": entry.task.priority,
                "type": entry.task.task_type,
                "reasoning": entry.reasoning,
            }
            for entry in self.entries
        ]


class Scheduler:
    """The brain: retrieves, organizes, and schedules tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[CareTask]:
        """Filter tasks by completion status, pet name, or both."""
        results: list[CareTask] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    @staticmethod
    def _to_minutes(time_str: str) -> int:
        """Convert 'HH:MM' to total minutes since midnight."""
        h, m = time_str.split(":")
        return int(h) * 60 + int(m)

    def detect_conflicts(self, schedule: DailySchedule) -> list[str]:
        """Return warning messages for any entries whose time ranges overlap."""
        warnings: list[str] = []
        for a, b in combinations(schedule.entries, 2):
            a_start = self._to_minutes(a.start_time)
            a_end = a_start + a.task.duration_minutes
            b_start = self._to_minutes(b.start_time)
            b_end = b_start + b.task.duration_minutes
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f'Conflict: "{a.task.title}" ({a.start_time}–{a_end // 60:02d}:{a_end % 60:02d}) '
                    f'overlaps with "{b.task.title}" ({b.start_time}–{b_end // 60:02d}:{b_end % 60:02d})'
                )
        return warnings

    def generate(self) -> DailySchedule:
        """Build a priority-sorted daily schedule that fits the owner's time budget."""
        pending = self.owner.get_all_pending_tasks()

        sorted_tasks = sorted(
            pending,
            key=lambda t: (-t.priority_rank(), t.duration_minutes),
        )

        fitted: list[CareTask] = []
        remaining = self.owner.available_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                fitted.append(task)
                remaining -= task.duration_minutes

        entries = self._assign_start_times(fitted)
        summary = (
            f"{len(entries)} of {len(pending)} pending tasks fit in "
            f"{self.owner.name}'s {self.owner.available_minutes}-minute window"
        )
        return DailySchedule(entries=entries, summary=summary)

    def _assign_start_times(self, tasks: list[CareTask]) -> list[ScheduledEntry]:
        """Assign sequential start times from 08:00 and attach reasoning text."""
        entries: list[ScheduledEntry] = []
        current_hour = 8
        current_minute = 0

        for task in tasks:
            start_time = f"{current_hour:02d}:{current_minute:02d}"
            reasoning = (
                f"{task.priority.capitalize()} priority {task.task_type} task "
                f"({task.duration_minutes} min) — scheduled next by rank"
            )
            entries.append(ScheduledEntry(
                task=task,
                start_time=start_time,
                reasoning=reasoning,
            ))
            total = current_minute + task.duration_minutes
            current_hour += total // 60
            current_minute = total % 60

        return entries
