import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task, TaskType, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Initialize session state ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# --- Owner setup ---
st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create owner"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner '{owner_name}' created.")

if st.session_state.owner is None:
    st.info("Enter your name above and click 'Create owner' to get started.")
    st.stop()

st.divider()

# --- Pet setup ---
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
pet_breed = st.text_input("Breed", value="Shiba Inu")
pet_age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    pet = Pet(name=pet_name, breed=pet_breed, age=pet_age)
    st.session_state.owner.add_pet(pet)
    st.success(f"Added pet '{pet_name}'.")

if st.session_state.owner.pets:
    st.write("Registered pets:")
    st.table([{"Name": p.name, "Breed": p.breed, "Age": p.age} for p in st.session_state.owner.pets])

st.divider()

# --- Task setup ---
st.subheader("Add a Task")

if not st.session_state.owner.pets:
    st.warning("Add at least one pet before adding tasks.")
    st.stop()

pet_names = [p.name for p in st.session_state.owner.pets]
selected_pet_name = st.selectbox("Assign to pet", pet_names)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority (1=low, 5=high)", [1, 2, 3, 4, 5], index=2)

task_type = st.selectbox("Task type", [t.value for t in TaskType])

if st.button("Add task"):
    target_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
    task = Task(
        task_type=TaskType(task_type),
        description=task_title,
        duration=int(duration),
        priority=priority,
        frequency=Frequency.DAILY,
    )
    st.session_state.scheduler.add_task(target_pet, task)
    st.success(f"Task '{task_title}' added to {selected_pet_name}.")

all_tasks = st.session_state.owner.get_all_tasks()
if all_tasks:
    st.write("All tasks:")
    st.table([
        {
            "Pet": next(p.name for p in st.session_state.owner.pets if task in p.tasks),
            "Type": task.task_type.value,
            "Description": task.description,
            "Duration (min)": task.duration,
            "Priority": task.priority,
        }
        for task in all_tasks
    ])

st.divider()

# --- Generate schedule ---
st.subheader("Generate Schedule")
available_hours = st.number_input("Your available hours today", min_value=1, max_value=24, value=8)

if st.button("Generate schedule"):
    from datetime import date
    plan = st.session_state.scheduler.generate_plan(
        target_date=date.today(),
        available_hours=int(available_hours),
    )
    st.markdown(f"### Daily Plan for {plan.date}")
    if plan.scheduled_tasks:
        st.table([
            {
                "Type": t.task_type.value,
                "Description": t.description,
                "Duration (min)": t.duration,
                "Priority": t.priority,
            }
            for t in plan.scheduled_tasks
        ])
    else:
        st.warning("No tasks could be scheduled. Add tasks or increase available hours.")
    st.info(plan.reasoning)
