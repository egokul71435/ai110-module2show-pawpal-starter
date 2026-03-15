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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        task_type = st.selectbox("Type", ["exercise", "feeding", "medication", "grooming", "enrichment"])

    if st.button("Add task"):
        selected_pet.add_task(CareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            task_type=task_type,
        ))

    # Display tasks per pet
    for pet in pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {
                    "task": t.title,
                    "duration": t.duration_minutes,
                    "priority": t.priority,
                    "type": t.task_type,
                    "done": t.completed,
                }
                for t in pet.tasks
            ])
else:
    st.info("Add a pet first, then you can assign tasks.")

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
        st.session_state.schedule = scheduler.generate()

# Display the schedule if one exists in session state
if st.session_state.schedule is not None:
    schedule: DailySchedule = st.session_state.schedule
    st.success(schedule.summary)
    st.table(schedule.to_dict_list())
