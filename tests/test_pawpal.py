from datetime import date

from pawpal_system import Pet, Task


def test_task_mark_complete_changes_status() -> None:
    task = Task("task-1", "Feed", date(2026, 10, 13), "08:00", "once", duration_minutes=10)

    task.mark_complete()

    assert task.completed is True


def test_pet_add_task_increases_task_count() -> None:
    pet = Pet("pet-1", "Mochi", "dog")
    task = Task("task-1", "Walk", date(2026, 10, 13), "08:00", "once", duration_minutes=20)

    pet.add_task(task)

    assert len(pet.tasks) == 1