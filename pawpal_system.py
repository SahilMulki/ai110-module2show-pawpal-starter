from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TaskType(Enum):
    WALK = "Walk"
    FEEDING = "Feeding"
    MEDICINE = "Medicine"
    GROOMING = "Grooming"
    VET_APPOINTMENT = "Vet Appointment"


@dataclass
class Pet:
    name: str
    breed: str
    age: int

    def walk(self) -> None:
        pass

    def eat(self) -> None:
        pass

    def sleep(self) -> None:
        pass


@dataclass
class Task:
    task_type: TaskType
    description: str
    duration: int      # minutes
    priority: int      # 1 (low) to 5 (high)

    def add_task(self) -> None:
        pass

    def edit_task(self) -> None:
        pass


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> None:
        pass


class Scheduler:
    def __init__(self) -> None:
        self.commitments: list[str] = []
        self.tasks: list[Task] = []

    def update_schedule(self) -> None:
        pass

    def show_schedule(self) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass


class Owner:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.pets: list[Pet] = []
        self.schedule: Optional[Scheduler] = None

    def add_pet(self, _pet: Pet) -> None:
        pass

    def remove_pet(self, _pet: Pet) -> None:
        pass

    def set_schedule(self, _schedule: Scheduler) -> None:
        pass
