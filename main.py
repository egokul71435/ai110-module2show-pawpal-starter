from pawpal_system import CareTask, DailySchedule, Owner, Pet, Scheduler, ScheduledEntry

# --- Setup owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Setup pets ---
mochi = Pet(name="Mochi", species="dog")
whiskers = Pet(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

# --- Add tasks OUT OF ORDER (mixed priorities, durations, frequencies) ---
whiskers.add_task(CareTask(
    title="Play with feather toy",
    duration_minutes=20,
    priority="medium",
    task_type="enrichment",
    frequency="daily",
))
mochi.add_task(CareTask(
    title="Brush fur",
    duration_minutes=15,
    priority="low",
    task_type="grooming",
    frequency="weekly",
))
whiskers.add_task(CareTask(
    title="Feed breakfast",
    duration_minutes=10,
    priority="high",
    task_type="feeding",
    frequency="daily",
))
mochi.add_task(CareTask(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    task_type="exercise",
    frequency="daily",
))
whiskers.add_task(CareTask(
    title="Administer flea meds",
    duration_minutes=5,
    priority="medium",
    task_type="medication",
    frequency="once",
))
mochi.add_task(CareTask(
    title="Evening walk",
    duration_minutes=25,
    priority="low",
    task_type="exercise",
    frequency="daily",
))

# --- Show tasks before completion ---
print("=== Before Completing Any Tasks ===")
print(f"  Mochi has {len(mochi.tasks)} tasks")
print(f"  Whiskers has {len(whiskers.tasks)} tasks")

# --- Complete tasks using Pet.complete_task() ---
print("\n=== Completing Tasks ===")

# Daily task — should auto-create next occurrence
next_task = mochi.complete_task("Morning walk")
print(f'  Completed "Morning walk" (daily)')
print(f"    Next occurrence due: {next_task.due_date}" if next_task else "    No recurrence")

# Weekly task — should auto-create next occurrence in 7 days
next_task = mochi.complete_task("Brush fur")
print(f'  Completed "Brush fur" (weekly)')
print(f"    Next occurrence due: {next_task.due_date}" if next_task else "    No recurrence")

# One-time task — should NOT create a next occurrence
next_task = whiskers.complete_task("Administer flea meds")
print(f'  Completed "Administer flea meds" (once)')
print(f"    Next occurrence due: {next_task.due_date}" if next_task else "    No recurrence")

# --- Show tasks after completion ---
print("\n=== After Completing Tasks ===")
print(f"  Mochi has {len(mochi.tasks)} tasks ({len(mochi.get_pending_tasks())} pending)")
for t in mochi.tasks:
    status = "[done]" if t.completed else "[ ]  "
    print(f"    {status} {t.title} (due {t.due_date}, {t.frequency})")

print(f"\n  Whiskers has {len(whiskers.tasks)} tasks ({len(whiskers.get_pending_tasks())} pending)")
for t in whiskers.tasks:
    status = "[done]" if t.completed else "[ ]  "
    print(f"    {status} {t.title} (due {t.due_date}, {t.frequency})")

# --- Generate schedule from pending tasks only ---
scheduler = Scheduler(owner)
schedule = scheduler.generate()

print(f"\n=== Today's Schedule for {owner.name} ===")
print(f"{schedule.summary}\n")

for entry in schedule.sort_by_time().entries:
    print(f"  {entry.start_time}  {entry.task.title} ({entry.task.duration_minutes} min, due {entry.task.due_date})")
    print(f"           {entry.reasoning}")
    print()

# --- Conflict detection: normal schedule (no overlaps expected) ---
conflicts = scheduler.detect_conflicts(schedule)
if conflicts:
    print("=== Conflicts Detected ===")
    for w in conflicts:
        print(f"  WARNING: {w}")
else:
    print("=== No Conflicts in Generated Schedule ===")

# --- Conflict detection: manually force overlapping entries ---
print("\n=== Forced Overlap Test ===")
walk = CareTask(title="Morning walk", duration_minutes=30, priority="high", task_type="exercise")
feed = CareTask(title="Feed breakfast", duration_minutes=15, priority="high", task_type="feeding")
groom = CareTask(title="Brush fur", duration_minutes=20, priority="low", task_type="grooming")

forced_schedule = DailySchedule(entries=[
    ScheduledEntry(task=walk,  start_time="08:00", reasoning="forced"),
    ScheduledEntry(task=feed,  start_time="08:10", reasoning="forced"),  # overlaps walk (08:00–08:30)
    ScheduledEntry(task=groom, start_time="08:20", reasoning="forced"),  # overlaps both
])

conflicts = scheduler.detect_conflicts(forced_schedule)
if conflicts:
    for w in conflicts:
        print(f"  WARNING: {w}")
else:
    print("  No conflicts found (unexpected!)")
