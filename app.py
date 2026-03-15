import streamlit as st
from pawpal_system import CareTask, DailySchedule, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant. Add your pets, assign tasks, and generate a daily schedule.")

# ---------------------------------------------------------------------------
# Session state initialization — create objects only if they don't exist yet
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

if "pets" not in st.session_state:
    st.session_state.pets = []

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "conflicts" not in st.session_state:
    st.session_state.conflicts = []

# Convenience references (refreshed every rerun, point to the same objects)
owner: Owner = st.session_state.owner
pets: list[Pet] = st.session_state.pets

st.divider()

# ---------------------------------------------------------------------------
# Owner + Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Setup")

owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=480, value=owner.available_minutes
)

st.markdown("#### Add a Pet")
col_pet1, col_pet2 = st.columns(2)
with col_pet1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col_pet2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if any(p.name == new_pet_name for p in pets):
        st.warning(f"A pet named **{new_pet_name}** already exists.")
    else:
        pet = Pet(name=new_pet_name, species=new_pet_species)
        pets.append(pet)
        owner.add_pet(pet)
        st.session_state.schedule = None  # clear stale schedule

if pets:
    st.write(f"**Registered pets:** {', '.join(p.name + ' (' + p.species + ')' for p in pets)}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Task management
# ---------------------------------------------------------------------------
st.subheader("Tasks")

if pets:
    pet_names = [p.name for p in pets]
    selected_pet_name = st.selectbox("Add task to pet", pet_names)
    selected_pet = next(p for p in pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_type = st.selectbox("Type", ["exercise", "feeding", "medication", "grooming", "enrichment"])
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        selected_pet.add_task(CareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            task_type=task_type,
            frequency=frequency,
        ))
        st.session_state.schedule = None  # clear stale schedule

    # Display tasks per pet with completion toggle
    for pet in pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            for i, task in enumerate(pet.tasks):
                col_check, col_info = st.columns([1, 5])
                with col_check:
                    done = st.checkbox(
                        "Done",
                        value=task.completed,
                        key=f"done_{pet.name}_{i}",
                        label_visibility="collapsed",
                    )
                with col_info:
                    status = "~~" if done else ""
                    st.markdown(
                        f"{status}**{task.title}** — {task.duration_minutes} min, "
                        f"{task.priority} priority, {task.task_type}, {task.frequency}{status}"
                    )
                    if task.completed != done:
                        if done:
                            next_task = pet.complete_task(task.title)
                            if next_task:
                                st.success(
                                    f"Recurring task! Next \"{task.title}\" "
                                    f"created for {next_task.due_date}"
                                )
                        else:
                            task.reset()
                        st.session_state.schedule = None
else:
    st.info("Add a pet first, then you can assign tasks.")

st.divider()

# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
if pets and owner.get_all_tasks():
    st.subheader("Filter Tasks")
    scheduler = Scheduler(owner)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in pets], key="filter_pet"
        )
    with col_f2:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Pending only", "Completed only"], key="filter_status"
        )

    pet_name_filter = None if filter_pet == "All pets" else filter_pet
    completed_filter = (
        None if filter_status == "All"
        else filter_status == "Completed only"
    )

    filtered = scheduler.filter_tasks(completed=completed_filter, pet_name=pet_name_filter)

    if filtered:
        st.table([
            {
                "task": t.title,
                "duration": t.duration_minutes,
                "priority": t.priority,
                "type": t.task_type,
                "frequency": t.frequency,
                "done": t.completed,
            }
            for t in filtered
        ])
    else:
        st.info("No tasks match the selected filters.")

    st.divider()

# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one pet with tasks first.")
    elif not owner.get_all_pending_tasks():
        st.warning("All tasks are complete — nothing to schedule.")
    else:
        scheduler = Scheduler(owner)
        schedule = scheduler.generate()
        st.session_state.schedule = schedule
        st.session_state.conflicts = scheduler.detect_conflicts(schedule)

# Display the schedule if one exists in session state
if st.session_state.schedule is not None:
    schedule: DailySchedule = st.session_state.schedule
    sorted_schedule = schedule.sort_by_time()

    st.success(sorted_schedule.summary)

    # Conflict warnings
    if st.session_state.conflicts:
        for warning in st.session_state.conflicts:
            st.warning(f"⏰ {warning}")
        st.caption(
            "Conflicts can occur when tasks are manually scheduled at overlapping times. "
            "Consider adjusting durations or staggering start times."
        )

    # Schedule table sorted chronologically
    st.table(sorted_schedule.to_dict_list())
