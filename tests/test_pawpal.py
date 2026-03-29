from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task, TaskType


# --- Helpers ---

def make_owner_with_pet():
    owner = Owner(name="Alex")
    pet = Pet(name="Luna", breed="Golden Retriever", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)
    return owner, pet, scheduler


# --- Original tests ---

def test_mark_complete_changes_status():
    task = Task(task_type=TaskType.WALK, description="Morning walk", duration=30, priority=3)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Luna", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0
    task = Task(task_type=TaskType.FEEDING, description="Feed Luna", duration=10, priority=5)
    pet.add_task(task)
    assert len(pet.tasks) == 1


# --- Priority / sorting ---

def test_generate_plan_sorts_by_priority():
    owner, pet, scheduler = make_owner_with_pet()
    scheduler.add_task(pet, Task(TaskType.GROOMING, "Grooming",  duration=10, priority=1))
    scheduler.add_task(pet, Task(TaskType.WALK,     "Walk",      duration=10, priority=4))
    scheduler.add_task(pet, Task(TaskType.MEDICINE, "Medicine",  duration=10, priority=5))
    scheduler.add_task(pet, Task(TaskType.FEEDING,  "Feeding",   duration=10, priority=3))

    plan = scheduler.generate_plan(target_date=date.today(), available_hours=8)
    priorities = [t.priority for t in plan.scheduled_tasks]
    assert priorities == sorted(priorities, reverse=True)


def test_pet_with_no_tasks_generates_empty_plan():
    owner, pet, scheduler = make_owner_with_pet()
    plan = scheduler.generate_plan(target_date=date.today(), available_hours=8)
    assert plan.scheduled_tasks == []


# --- Recurrence ---

def test_complete_daily_task_creates_recurrence():
    owner, pet, scheduler = make_owner_with_pet()
    today = date.today()
    task = Task(TaskType.WALK, "Walk Luna", duration=30, priority=3,
                frequency=Frequency.DAILY, due_date=today)
    scheduler.add_task(pet, task)

    next_task = scheduler.complete_task(task, pet)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_complete_as_needed_task_no_recurrence():
    owner, pet, scheduler = make_owner_with_pet()
    task = Task(TaskType.VET_APPOINTMENT, "Vet visit", duration=60, priority=3,
                frequency=Frequency.AS_NEEDED)
    scheduler.add_task(pet, task)

    next_task = scheduler.complete_task(task, pet)

    assert task.completed is True
    assert next_task is None
    assert len(pet.tasks) == 1  # no new task added


# --- Conflict detection ---

def test_conflict_detection_same_start_time():
    owner, pet, scheduler = make_owner_with_pet()
    scheduler.add_task(pet, Task(TaskType.WALK,    "Walk",    duration=30, priority=4,
                                 preferred_time=time(8, 0)))
    scheduler.add_task(pet, Task(TaskType.FEEDING, "Feeding", duration=15, priority=5,
                                 preferred_time=time(8, 0)))

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feeding" in conflicts[0]


def test_conflict_detection_no_overlap():
    owner, pet, scheduler = make_owner_with_pet()
    scheduler.add_task(pet, Task(TaskType.WALK,    "Walk",    duration=30, priority=4,
                                 preferred_time=time(7, 0)))   # 07:00–07:30
    scheduler.add_task(pet, Task(TaskType.FEEDING, "Feeding", duration=15, priority=5,
                                 preferred_time=time(7, 30)))  # 07:30–07:45 — adjacent, not overlapping

    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


# --- Time budget ---

def test_plan_respects_available_time_limit():
    owner, pet, scheduler = make_owner_with_pet()
    scheduler.add_task(pet, Task(TaskType.WALK,     "Walk",     duration=50, priority=4))
    scheduler.add_task(pet, Task(TaskType.GROOMING, "Grooming", duration=50, priority=3))
    scheduler.add_task(pet, Task(TaskType.MEDICINE, "Medicine", duration=50, priority=5))

    # 2 hours = 120 min; only 2 of the 3 tasks (150 min total) should fit
    plan = scheduler.generate_plan(target_date=date.today(), available_hours=2)
    total_duration = sum(t.duration for t in plan.scheduled_tasks)
    assert total_duration <= 120
    assert len(plan.scheduled_tasks) == 2
