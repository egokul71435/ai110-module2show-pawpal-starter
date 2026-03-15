from pawpal_system import CareTask, Owner, Pet, Scheduler

# --- Setup owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Setup pets ---
mochi = Pet(name="Mochi", species="dog")
whiskers = Pet(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

# --- Add tasks to Mochi ---
mochi.add_task(CareTask(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    task_type="exercise",
))
mochi.add_task(CareTask(
    title="Brush fur",
    duration_minutes=15,
    priority="low",
    task_type="grooming",
))

# --- Add tasks to Whiskers ---
whiskers.add_task(CareTask(
    title="Feed breakfast",
    duration_minutes=10,
    priority="high",
    task_type="feeding",
))
whiskers.add_task(CareTask(
    title="Administer flea meds",
    duration_minutes=5,
    priority="medium",
    task_type="medication",
))
whiskers.add_task(CareTask(
    title="Play with feather toy",
    duration_minutes=20,
    priority="medium",
    task_type="enrichment",
))

# --- Generate and print schedule ---
scheduler = Scheduler(owner)
schedule = scheduler.generate()

print(f"=== Today's Schedule for {owner.name} ===")
print(f"{schedule.summary}\n")

for entry in schedule.entries:
    print(f"  {entry.start_time}  {entry.task.title} ({entry.task.duration_minutes} min)")
    print(f"           {entry.reasoning}")
    print()
