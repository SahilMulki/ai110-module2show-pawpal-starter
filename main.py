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

# --- Tasks added intentionally out of priority order ---

# Luna: low priority added first, high priority last
scheduler.add_task(luna, Task(
    task_type=TaskType.GROOMING,
    description="Brush Luna's coat",
    duration=20,
    priority=2,
    frequency=Frequency.WEEKLY,
    preferred_time=time(17, 0),
))
scheduler.add_task(luna, Task(
    task_type=TaskType.WALK,
    description="Morning walk with Luna",
    duration=30,
    priority=4,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 0),
))
scheduler.add_task(luna, Task(
    task_type=TaskType.MEDICINE,
    description="Luna's flea prevention medicine",
    duration=10,
    priority=5,
    frequency=Frequency.MONTHLY,
    preferred_time=time(8, 0),
))

# Max: medium priority added first, highest last
scheduler.add_task(max_, Task(
    task_type=TaskType.VET_APPOINTMENT,
    description="Max's annual checkup",
    duration=60,
    priority=3,
    frequency=Frequency.AS_NEEDED,
    preferred_time=time(14, 0),
))
scheduler.add_task(max_, Task(
    task_type=TaskType.GROOMING,
    description="Trim Max's nails",
    duration=15,
    priority=1,
    frequency=Frequency.MONTHLY,
    preferred_time=time(16, 0),
))
scheduler.add_task(max_, Task(
    task_type=TaskType.FEEDING,
    description="Feed Max (wet food)",
    duration=10,
    priority=5,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 30),
))

# --- Intentional conflict: Luna's grooming (07:15–07:35) overlaps her walk (07:00–07:30) ---
scheduler.add_task(luna, Task(
    task_type=TaskType.GROOMING,
    description="Quick brush before walk",
    duration=20,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 15),  # starts at 07:15, walk ends at 07:30 → overlap
))

# --- Conflict detection ---
print("Conflict Detection")
print("=" * 40)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts detected.")

# --- Mark a couple tasks complete to test completion filtering ---
luna.tasks[0].mark_complete()   # Brush Luna's coat → completed
max_.tasks[1].mark_complete()   # Trim Max's nails  → completed

# --- Owner has a work commitment that blocks time ---
scheduler.add_commitment(Commitment(
    label="Work",
    start_time=time(9, 0),
    end_time=time(17, 0),
))

# --- filter_tasks demos ---
def print_tasks(label: str, tasks: list) -> None:
    print(f"\n{label}")
    print("-" * 40)
    if not tasks:
        print("  (none)")
    for t in tasks:
        status = "[x]" if t.completed else "[ ]"
        print(f"  {status} p{t.priority} [{t.task_type.value}] {t.description}")

# 1. All incomplete tasks across all pets (unsorted raw order)
print_tasks(
    "All INCOMPLETE tasks (all pets)",
    scheduler.filter_tasks(completed=False),
)

# 2. All completed tasks across all pets
print_tasks(
    "All COMPLETED tasks (all pets)",
    scheduler.filter_tasks(completed=True),
)

# 3. All tasks for Luna only
print_tasks(
    "All tasks for Luna",
    scheduler.filter_tasks(pet_name="Luna"),
)

# 4. Incomplete tasks for Max only
print_tasks(
    "INCOMPLETE tasks for Max",
    scheduler.filter_tasks(completed=False, pet_name="Max"),
)

# --- Generate and display today's plan (priority-sorted by scheduler) ---
plan = scheduler.generate_plan(target_date=date.today(), available_hours=12)

print("\n\nToday's Schedule")
print("=" * 40)
scheduler.show_schedule()
plan.display()
