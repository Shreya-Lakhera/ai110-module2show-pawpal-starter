import streamlit as st

from datetime import date, time
from uuid import uuid4

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

def task_details(task: Task) -> str:
    """Format a task for a select box."""
    status = "complete" if task.completed else "incomplete"
    return f"{task.description} | {task.due_date} {task.time} | {status}"

def find_pet_for_task(owner: Owner, task_id: str) -> Pet | None:
    """Find the pet that owns a task ID."""
    for pet, task in owner.get_all_tasks():
        if task.id == task_id:
            return pet
    return None

def display_task(task: Task, pet_name: str) -> None:
    """Display one task in a readable format."""
    status = "Complete" if task.completed else "Incomplete"
    st.write(
        f"**{pet_name}** | {task.description} | {task.due_date} at {task.time} | "
        f"{task.duration_minutes} min | {task.priority} priority | {task.frequency} | {status}"
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", 60)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("PawPal+")
st.caption(
    "Plan care tasks for your pets. Session state retains your data during this session, "
    "but it does not provide permanent storage."
)

st.header("Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name)
    available_minutes = st.number_input(
        "Available care minutes",
        min_value=0,
        value=owner.available_minutes,
        step=5,
    )
    save_owner = st.form_submit_button("Save owner settings")

if save_owner:
    try:
        updated_owner = Owner(owner_name, int(available_minutes))
        owner.name = updated_owner.name
        owner.available_minutes = updated_owner.available_minutes
        st.success("Owner settings saved.")
    except ValueError as error:
        st.error(str(error))

st.header("Pets")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", key="new_pet_name")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    try:
        owner.add_pet(Pet(uuid4().hex, pet_name, species))
        st.success(f"Added {pet_name.strip()}.")
    except ValueError as error:
        st.error(str(error))

if owner.pets:
    pet_options = {pet.id: pet.name for pet in owner.pets}
    st.write("Pets:", ", ".join(pet.name for pet in owner.pets))

    st.header("Add task")
    with st.form("task_form", clear_on_submit=True):
        selected_pet_id = st.selectbox(
            "Pet", list(pet_options), format_func=pet_options.get, key="task_pet"
        )
        description = st.text_input("Task description", key="new_task_description")
        due_date = st.date_input("Due date", value=date.today(), key="new_task_date")
        task_time = st.time_input("Time", value=time(8, 0), key="new_task_time")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=1440, value=20, key="new_task_duration"
        )
        priority = st.selectbox(
            "Priority", ["high", "medium", "low"], key="new_task_priority"
        )
        frequency = st.selectbox(
            "Frequency", ["once", "daily", "weekly"], key="new_task_frequency"
        )
        add_task = st.form_submit_button("Add task")

    if add_task:
        try:
            task = Task(
                uuid4().hex,
                description,
                due_date,
                task_time.strftime("%H:%M"),
                frequency,
                duration_minutes=int(duration),
                priority=priority,
            )
            next((pet for pet in owner.pets if pet.id == selected_pet_id)).add_task(task)
            st.success(f"Added task '{task.description.strip()}'.")
        except ValueError as error:
            st.error(str(error))

    all_pairs = owner.get_all_tasks()
    incomplete_pairs = [(pet, task) for pet, task in all_pairs if not task.completed]

    if incomplete_pairs:
        st.header("Edit an incomplete task")
        incomplete_by_id = {task.id: (pet, task) for pet, task in incomplete_pairs}
        with st.form("edit_task_form"):
            edit_id = st.selectbox(
                "Task to edit",
                list(incomplete_by_id),
                format_func=lambda task_id: task_details(incomplete_by_id[task_id][1]),
                key="edit_task_id",
            )
            edit_pet, existing_task = incomplete_by_id[edit_id]
            edit_description = st.text_input(
                "Description", value=existing_task.description, key="edit_description"
            )
            edit_date = st.date_input(
                "Due date", value=existing_task.due_date, key="edit_date"
            )
            edit_time = st.time_input(
                "Time",
                value=time.fromisoformat(existing_task.time),
                key="edit_time",
            )
            edit_duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=1440,
                value=existing_task.duration_minutes,
                key="edit_duration",
            )
            edit_priority = st.selectbox(
                "Priority",
                ["high", "medium", "low"],
                index=["high", "medium", "low"].index(existing_task.priority),
                key="edit_priority",
            )
            edit_frequency = st.selectbox(
                "Frequency",
                ["once", "daily", "weekly"],
                index=["once", "daily", "weekly"].index(existing_task.frequency),
                key="edit_frequency",
            )
            save_edit = st.form_submit_button("Save task changes")

        if save_edit:
            try:
                updated_task = Task(
                    edit_id,
                    edit_description,
                    edit_date,
                    edit_time.strftime("%H:%M"),
                    edit_frequency,
                    duration_minutes=int(edit_duration),
                    priority=edit_priority,
                )
                edit_pet.edit_task(edit_id, updated_task)
                st.success("Task changes saved.")
            except ValueError as error:
                st.error(str(error))

        st.header("Complete a task")
        complete_by_id = {task.id: (pet, task) for pet, task in incomplete_pairs}
        with st.form("complete_task_form"):
            complete_id = st.selectbox(
                "Task to complete",
                list(complete_by_id),
                format_func=lambda task_id: task_details(complete_by_id[task_id][1]),
                key="complete_task_id",
            )
            complete_task = st.form_submit_button("Mark task complete")

        if complete_task:
            try:
                scheduler.mark_task_complete(complete_id)
                st.success("Task completed. A new occurrence was added for recurring tasks.")
            except ValueError as error:
                st.error(str(error))
    else:
        st.info("No incomplete tasks are available to edit or complete.")
else:
    st.info("Add a pet before creating care tasks.")

st.header("Tasks")
if owner.get_all_tasks():
    st.subheader("Sorted schedule")
    for task in scheduler.sort_by_time():
        pet = find_pet_for_task(owner, task.id)
        if pet is not None:
            display_task(task, pet.name)

    st.subheader("Filter tasks")
    pet_filter_options = {"all": "All pets"}
    pet_filter_options.update({pet.id: pet.name for pet in owner.pets})
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        selected_filter_pet = st.selectbox(
            "Pet filter",
            list(pet_filter_options),
            format_func=pet_filter_options.get,
            key="filter_pet",
        )
    with filter_col2:
        selected_status = st.selectbox(
            "Completion filter",
            ["all", "incomplete", "complete"],
            format_func=lambda value: value.title(),
            key="filter_status",
        )
    with filter_col3:
        use_date_filter = st.checkbox("Filter by selected date", value=True, key="use_date_filter")
        selected_filter_date = st.date_input(
            "Selected date", value=date.today(), key="filter_date"
        )

    completed_filter = {"all": None, "incomplete": False, "complete": True}[selected_status]
    filtered_tasks = scheduler.filter_tasks(
        pet_id=None if selected_filter_pet == "all" else selected_filter_pet,
        completed=completed_filter,
        due_date=selected_filter_date if use_date_filter else None,
    )
    if filtered_tasks:
        for task in filtered_tasks:
            pet = find_pet_for_task(owner, task.id)
            if pet is not None:
                display_task(task, pet.name)
    else:
        st.info("No tasks match the selected filters.")
else:
    st.info("No tasks yet. Add a pet and then add a care task.")

st.header("Schedule checks")
for warning in scheduler.detect_conflicts():
    st.warning(warning)
if not scheduler.detect_conflicts():
    st.success("No exact start-time conflicts found.")

st.header("Daily plan")
plan_date = st.date_input("Plan date", value=date.today(), key="plan_date")
if st.button("Generate daily plan", key="generate_plan"):
    selected_tasks, skipped_tasks = scheduler.generate_daily_plan(
        plan_date, owner.available_minutes
    )
    st.write(
        f"Using {owner.available_minutes} available minutes, PawPal+ considers high priority "
        "tasks first, then medium and low priority tasks, and displays selected tasks in time order."
    )
    st.subheader("Selected tasks")
    if selected_tasks:
        for task in selected_tasks:
            pet = find_pet_for_task(owner, task.id)
            if pet is not None:
                display_task(task, pet.name)
    else:
        st.info("No tasks fit the available time budget on this date.")

    st.subheader("Skipped tasks")
    if skipped_tasks:
        for task in skipped_tasks:
            pet = find_pet_for_task(owner, task.id)
            if pet is not None:
                st.write(
                    f"**{pet.name}** | {task.description} | {task.duration_minutes} min "
                    "(exceeds the remaining time budget)"
                )
    else:
        st.write("No tasks were skipped.")
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
