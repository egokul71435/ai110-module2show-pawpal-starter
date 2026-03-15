from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class CareTask:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    task_type: str
    frequency: str = "daily"
    completed: bool = False

    def priority_rank(self) -> int:
        """Return a numeric score for sorting: high=3, medium=2, low=1."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
