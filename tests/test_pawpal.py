from pawpal_system import Frequency, Pet, Task, TaskType


def test_mark_complete_changes_status():
    task = Task(
        task_type=TaskType.WALK,
        description="Morning walk",
        duration=30,
        priority=3,
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Luna", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0

    task = Task(
        task_type=TaskType.FEEDING,
        description="Feed Luna",
        duration=10,
        priority=5,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)
    assert len(pet.tasks) == 1
