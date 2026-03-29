from datetime import date, time

from pawpal_system import (
    Commitment,
    Frequency,
    Owner,
    Pet,
    Scheduler,
    Task,
    TaskType,
)

# --- Setup ---
owner = Owner(name="Alex")

luna = Pet(name="Luna", breed="Golden Retriever", age=3)
max_ = Pet(name="Max", breed="Tabby Cat", age=5)

owner.add_pet(luna)
owner.add_pet(max_)

scheduler = Scheduler(owner=owner)
owner.set_schedule(scheduler)

# --- Tasks for Luna ---
morning_walk = Task(
    task_type=TaskType.WALK,
    description="Morning walk with Luna",
    duration=30,
    priority=4,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 0),
)

luna_medicine = Task(
    task_type=TaskType.MEDICINE,
    description="Luna's flea prevention medicine",
    duration=10,
    priority=5,
    frequency=Frequency.MONTHLY,
    preferred_time=time(8, 0),
)

luna_grooming = Task(
    task_type=TaskType.GROOMING,
    description="Brush Luna's coat",
    duration=20,
    priority=2,
    frequency=Frequency.WEEKLY,
    preferred_time=time(17, 0),
)

# --- Tasks for Max ---
max_feeding = Task(
    task_type=TaskType.FEEDING,
    description="Feed Max (wet food)",
    duration=10,
    priority=5,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 30),
)

max_vet = Task(
    task_type=TaskType.VET_APPOINTMENT,
    description="Max's annual checkup",
    duration=60,
    priority=3,
    frequency=Frequency.AS_NEEDED,
    preferred_time=time(14, 0),
)

# --- Register tasks via Scheduler ---
scheduler.add_task(luna, morning_walk)
scheduler.add_task(luna, luna_medicine)
scheduler.add_task(luna, luna_grooming)
scheduler.add_task(max_, max_feeding)
scheduler.add_task(max_, max_vet)

# --- Owner has a work commitment that blocks time ---
scheduler.add_commitment(Commitment(
    label="Work",
    start_time=time(9, 0),
    end_time=time(17, 0),
))

# --- Generate and display today's plan ---
plan = scheduler.generate_plan(target_date=date.today(), available_hours=12)

print("Today's Schedule")
print("=" * 40)
scheduler.show_schedule()
plan.display()
