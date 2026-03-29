from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Optional


class TaskType(Enum):
    WALK = "Walk"
    FEEDING = "Feeding"
    MEDICINE = "Medicine"
    GROOMING = "Grooming"
    VET_APPOINTMENT = "Vet Appointment"


class Frequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    AS_NEEDED = "As Needed"


@dataclass
class Commitment:
    label: str
    start_time: time
    end_time: time

    def duration_minutes(self) -> int:
        """Return the length of this commitment in minutes."""
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        return max(0, end - start)


@dataclass
class Task:
    task_type: TaskType
    description: str
    duration: int                           # minutes
    priority: int                           # 1 (low) to 5 (high)
    frequency: Frequency = Frequency.DAILY
    preferred_time: Optional[time] = None   # ideal start time (e.g. 08:00 for medicine)
    time_window: Optional[tuple[time, time]] = None  # allowed window (start, end)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete (e.g. for a new day)."""
        self.completed = False


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks for this pet that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def walk(self) -> Task:
        """Convenience: create and register a default walk task for this pet."""
        task = Task(
            task_type=TaskType.WALK,
            description=f"Walk {self.name}",
            duration=30,
            priority=3,
            frequency=Frequency.DAILY,
        )
        self.add_task(task)
        return task

    def eat(self) -> Task:
        """Convenience: create and register a default feeding task for this pet."""
        task = Task(
            task_type=TaskType.FEEDING,
            description=f"Feed {self.name}",
            duration=15,
            priority=5,
            frequency=Frequency.DAILY,
        )
        self.add_task(task)
        return task

    def sleep(self) -> None:
        """Sleep is a natural behavior — no task required."""
        pass


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> None:
        """Print the daily plan and scheduling reasoning to the terminal."""
        print(f"\n=== Daily Plan for {self.date} ===")
        if not self.scheduled_tasks:
            print("  No tasks scheduled.")
        else:
            for i, task in enumerate(self.scheduled_tasks, 1):
                time_str = (
                    f" @ {task.preferred_time.strftime('%H:%M')}"
                    if task.preferred_time
                    else ""
                )
                status = "[x]" if task.completed else "[ ]"
                print(
                    f"  {i}. {status} [{task.task_type.value}] {task.description}"
                    f"{time_str} — {task.duration} min, priority {task.priority}"
                )
        if self.reasoning:
            print(f"\n  Reasoning: {self.reasoning}")


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an owner and an empty commitments list."""
        self.owner: Owner = owner
        self.commitments: list[Commitment] = []

    @property
    def tasks(self) -> list[Task]:
        """All tasks across every pet the owner has."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task directly to a specific pet."""
        pet.add_task(task)

    def edit_task(self, task: Task, **updates) -> None:
        """Update any Task field by keyword, e.g. edit_task(t, priority=5, duration=20)."""
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

    def add_commitment(self, commitment: Commitment) -> None:
        """Register a time block that reduces the owner's available scheduling time."""
        self.commitments.append(commitment)

    def _committed_minutes(self) -> int:
        """Return the total minutes consumed by all commitments."""
        return sum(c.duration_minutes() for c in self.commitments)

    def _free_minutes(self, available_hours: int) -> int:
        """Return available minutes after subtracting all commitments."""
        return max(0, available_hours * 60 - self._committed_minutes())

    def update_schedule(self) -> None:
        """Reset all task completion statuses (e.g. at the start of a new day)."""
        for task in self.tasks:
            task.mark_incomplete()

    def show_schedule(self) -> None:
        """Print all tasks grouped by pet."""
        if not self.owner.pets:
            print("No pets registered.")
            return
        for pet in self.owner.pets:
            print(f"\n{pet.name} ({pet.breed}, age {pet.age}):")
            if not pet.tasks:
                print("  No tasks.")
                continue
            for task in pet.tasks:
                status = "[x]" if task.completed else "[ ]"
                print(
                    f"  {status} [{task.task_type.value}] {task.description}"
                    f" — {task.duration} min, priority {task.priority}, {task.frequency.value}"
                )

    def generate_plan(self, target_date: date, available_hours: int) -> DailyPlan:
        """Build a DailyPlan by fitting highest-priority tasks into the owner's free time."""
        free_minutes = self._free_minutes(available_hours)

        pending = sorted(
            [t for t in self.tasks if not t.completed],
            key=lambda t: t.priority,
            reverse=True,
        )

        scheduled: list[Task] = []
        minutes_used = 0
        skipped: list[Task] = []

        for task in pending:
            if minutes_used + task.duration <= free_minutes:
                scheduled.append(task)
                minutes_used += task.duration
            else:
                skipped.append(task)

        reasoning_parts = [
            f"{self.owner.name} has {available_hours}h available "
            f"({free_minutes} min after {len(self.commitments)} commitment(s)).",
            f"Scheduled {len(scheduled)} task(s) using {minutes_used} min.",
        ]
        if skipped:
            skipped_names = ", ".join(t.description for t in skipped)
            reasoning_parts.append(f"Skipped due to time: {skipped_names}.")

        return DailyPlan(
            date=target_date,
            scheduled_tasks=scheduled,
            reasoning=" ".join(reasoning_parts),
        )


class Owner:
    def __init__(self, name: str) -> None:
        """Initialize an Owner with a name and empty pets and schedule."""
        self.name: str = name
        self.pets: list[Pet] = []
        self.schedule: Optional[Scheduler] = None

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self.pets.remove(pet)

    def set_schedule(self, schedule: Scheduler) -> None:
        """Attach a Scheduler instance to this owner."""
        self.schedule = schedule

    def get_all_tasks(self) -> list[Task]:
        """Flat list of every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]
