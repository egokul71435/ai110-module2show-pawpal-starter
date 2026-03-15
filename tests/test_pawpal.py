from datetime import date, timedelta

from pawpal_system import (
    CareTask,
    DailySchedule,
    Owner,
    Pet,
    ScheduledEntry,
    Scheduler,
)


# ---- Existing tests --------------------------------------------------------

def test_mark_complete_changes_status():
    task = CareTask(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        task_type="exercise",
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(CareTask(
        title="Feed breakfast",
        duration_minutes=10,
        priority="high",
        task_type="feeding",
    ))
    assert len(pet.tasks) == 1

    pet.add_task(CareTask(
        title="Brush fur",
        duration_minutes=15,
        priority="low",
        task_type="grooming",
    ))
    assert len(pet.tasks) == 2


# ---- Sorting correctness ---------------------------------------------------

def test_generate_sorts_by_priority():
    """High-priority tasks appear before medium, which appear before low."""
    owner = Owner(name="Jo", available_minutes=120)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    pet.add_task(CareTask(title="Groom", duration_minutes=10, priority="low", task_type="grooming"))
    pet.add_task(CareTask(title="Feed", duration_minutes=10, priority="high", task_type="feeding"))
    pet.add_task(CareTask(title="Play", duration_minutes=10, priority="medium", task_type="enrichment"))

    schedule = Scheduler(owner).generate()
    titles = [e.task.title for e in schedule.entries]
    assert titles == ["Feed", "Play", "Groom"]


def test_generate_breaks_ties_by_duration():
    """Within the same priority, shorter tasks come first."""
    owner = Owner(name="Jo", available_minutes=120)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    pet.add_task(CareTask(title="Long walk", duration_minutes=40, priority="high", task_type="exercise"))
    pet.add_task(CareTask(title="Quick feed", duration_minutes=5, priority="high", task_type="feeding"))

    schedule = Scheduler(owner).generate()
    titles = [e.task.title for e in schedule.entries]
    assert titles == ["Quick feed", "Long walk"]


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() reorders entries by their HH:MM start_time."""
    task_a = CareTask(title="A", duration_minutes=10, priority="high", task_type="feeding")
    task_b = CareTask(title="B", duration_minutes=10, priority="high", task_type="feeding")
    task_c = CareTask(title="C", duration_minutes=10, priority="high", task_type="feeding")

    schedule = DailySchedule(entries=[
        ScheduledEntry(task=task_c, start_time="10:30", reasoning=""),
        ScheduledEntry(task=task_a, start_time="08:00", reasoning=""),
        ScheduledEntry(task=task_b, start_time="09:15", reasoning=""),
    ])

    sorted_schedule = schedule.sort_by_time()
    times = [e.start_time for e in sorted_schedule.entries]
    assert times == ["08:00", "09:15", "10:30"]


# ---- Recurrence logic -------------------------------------------------------

def test_daily_task_recurs_next_day():
    """Completing a daily task creates a new instance due tomorrow."""
    today = date.today()
    task = CareTask(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        task_type="exercise",
        frequency="daily",
        due_date=today,
    )
    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.title == task.title


def test_weekly_task_recurs_in_seven_days():
    """Completing a weekly task creates a new instance due in 7 days."""
    today = date.today()
    task = CareTask(
        title="Brush fur",
        duration_minutes=15,
        priority="low",
        task_type="grooming",
        frequency="weekly",
        due_date=today,
    )
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_does_not_recur():
    """Completing a one-time task returns None (no next occurrence)."""
    task = CareTask(
        title="Vet visit",
        duration_minutes=60,
        priority="high",
        task_type="medication",
        frequency="once",
    )
    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is None


def test_pet_complete_task_appends_next_occurrence():
    """Pet.complete_task() marks done AND adds the recurring copy to its list."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(CareTask(
        title="Walk",
        duration_minutes=20,
        priority="high",
        task_type="exercise",
        frequency="daily",
    ))
    assert len(pet.tasks) == 1

    pet.complete_task("Walk")

    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


# ---- Conflict detection -----------------------------------------------------

def test_overlapping_tasks_detected():
    """Two entries whose time ranges overlap produce a conflict warning."""
    owner = Owner(name="Jo", available_minutes=60)
    scheduler = Scheduler(owner)

    task_a = CareTask(title="Walk", duration_minutes=30, priority="high", task_type="exercise")
    task_b = CareTask(title="Feed", duration_minutes=20, priority="high", task_type="feeding")

    schedule = DailySchedule(entries=[
        ScheduledEntry(task=task_a, start_time="08:00", reasoning=""),
        ScheduledEntry(task=task_b, start_time="08:15", reasoning=""),  # overlaps 08:00–08:30
    ])

    conflicts = scheduler.detect_conflicts(schedule)
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


def test_adjacent_tasks_no_conflict():
    """Two entries that are back-to-back (no overlap) produce no warnings."""
    owner = Owner(name="Jo", available_minutes=60)
    scheduler = Scheduler(owner)

    task_a = CareTask(title="Walk", duration_minutes=30, priority="high", task_type="exercise")
    task_b = CareTask(title="Feed", duration_minutes=15, priority="high", task_type="feeding")

    schedule = DailySchedule(entries=[
        ScheduledEntry(task=task_a, start_time="08:00", reasoning=""),
        ScheduledEntry(task=task_b, start_time="08:30", reasoning=""),  # starts exactly when Walk ends
    ])

    conflicts = scheduler.detect_conflicts(schedule)
    assert len(conflicts) == 0


def test_exact_same_start_time_detected():
    """Two tasks starting at the exact same time are flagged as a conflict."""
    owner = Owner(name="Jo", available_minutes=60)
    scheduler = Scheduler(owner)

    task_a = CareTask(title="Walk", duration_minutes=20, priority="high", task_type="exercise")
    task_b = CareTask(title="Feed", duration_minutes=10, priority="high", task_type="feeding")

    schedule = DailySchedule(entries=[
        ScheduledEntry(task=task_a, start_time="08:00", reasoning=""),
        ScheduledEntry(task=task_b, start_time="08:00", reasoning=""),
    ])

    conflicts = scheduler.detect_conflicts(schedule)
    assert len(conflicts) == 1


# ---- Edge cases --------------------------------------------------------------

def test_pet_with_no_tasks_produces_empty_schedule():
    """An owner whose pets have no tasks gets an empty schedule."""
    owner = Owner(name="Jo", available_minutes=60)
    owner.add_pet(Pet(name="Rex", species="dog"))

    schedule = Scheduler(owner).generate()
    assert len(schedule.entries) == 0
    assert "0 of 0" in schedule.summary


def test_zero_available_minutes_schedules_nothing():
    """An owner with zero free time gets no tasks scheduled."""
    owner = Owner(name="Jo", available_minutes=0)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(CareTask(title="Walk", duration_minutes=10, priority="high", task_type="exercise"))

    schedule = Scheduler(owner).generate()
    assert len(schedule.entries) == 0


def test_all_completed_tasks_produces_empty_schedule():
    """If every task is already done, the schedule has nothing to plan."""
    owner = Owner(name="Jo", available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    task = CareTask(title="Walk", duration_minutes=10, priority="high", task_type="exercise", frequency="once")
    task.mark_complete()
    pet.add_task(task)

    schedule = Scheduler(owner).generate()
    assert len(schedule.entries) == 0
