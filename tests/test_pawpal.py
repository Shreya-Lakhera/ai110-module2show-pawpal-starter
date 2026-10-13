from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete_changes_status() -> None:
    task = Task("task-1", "Feed", date(2026, 10, 13), "08:00", "once", duration_minutes=10)

    task.mark_complete()

    assert task.completed is True


def test_pet_add_task_increases_task_count() -> None:
    pet = Pet("pet-1", "Mochi", "dog")
    task = Task("task-1", "Walk", date(2026, 10, 13), "08:00", "once", duration_minutes=20)

    pet.add_task(task)

    assert len(pet.tasks) == 1


def make_task(
    task_id: str,
    description: str,
    due_date: date,
    task_time: str = "09:00",
    frequency: str = "once",
    *,
    duration: int = 10,
    priority: str = "medium",
    completed: bool = False,
) -> Task:
    """Create a valid task for a test."""
    return Task(
        task_id,
        description,
        due_date,
        task_time,
        frequency,
        completed=completed,
        duration_minutes=duration,
        priority=priority,
    )


def make_owner_with_pets() -> tuple[Owner, Pet, Pet, Scheduler]:
    """Create an independent owner with two pets."""
    owner = Owner("Jordan", 60)
    first_pet = Pet("pet-1", "Mochi", "dog")
    second_pet = Pet("pet-2", "Luna", "cat")
    owner.add_pet(first_pet)
    owner.add_pet(second_pet)
    return owner, first_pet, second_pet, Scheduler(owner)


def test_sorting_tasks_added_out_of_order() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    first = make_task("first", "First", date(2026, 10, 14), "08:00")
    second = make_task("second", "Second", date(2026, 10, 13), "12:00")
    third = make_task("third", "Third", date(2026, 10, 13), "07:00")
    pet.tasks.extend([first, second, third])

    sorted_tasks = Scheduler(owner).sort_by_time()

    assert [task.id for task in sorted_tasks] == ["third", "second", "first"]
    assert [task.id for task in pet.tasks] == ["first", "second", "third"]


def test_aggregates_and_sorts_tasks_across_two_pets() -> None:
    owner, first_pet, second_pet, scheduler = make_owner_with_pets()
    first_pet.add_task(make_task("dog-task", "Dog walk", date(2026, 10, 13), "10:00"))
    second_pet.add_task(make_task("cat-task", "Cat feeding", date(2026, 10, 13), "08:00"))

    pairs = owner.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time()

    assert [(pet.id, task.id) for pet, task in pairs] == [
        ("pet-1", "dog-task"),
        ("pet-2", "cat-task"),
    ]
    assert [task.id for task in sorted_tasks] == ["cat-task", "dog-task"]


def test_filters_by_pet_completion_status_and_date() -> None:
    owner, first_pet, second_pet, scheduler = make_owner_with_pets()
    target_date = date(2026, 10, 13)
    first_pet.add_task(make_task("dog-open", "Open dog task", target_date))
    first_pet.add_task(make_task("dog-done", "Done dog task", target_date, completed=True))
    second_pet.add_task(make_task("cat-other-day", "Cat task", date(2026, 10, 14)))

    assert [task.id for task in scheduler.filter_tasks(pet_id="pet-1")] == [
        "dog-open",
        "dog-done",
    ]
    assert [task.id for task in scheduler.filter_tasks(completed=False)] == [
        "dog-open",
        "cat-other-day",
    ]
    assert [task.id for task in scheduler.filter_tasks(due_date=target_date)] == [
        "dog-open",
        "dog-done",
    ]


def test_daily_recurrence_creates_one_new_incomplete_task_tomorrow() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    original = make_task("daily-1", "Walk", date(2026, 10, 13), "08:00", "daily")
    pet.add_task(original)

    Scheduler(owner).mark_task_complete("daily-1")

    assert len(pet.tasks) == 2
    occurrence = pet.tasks[1]
    assert original.completed is True
    assert occurrence.completed is False
    assert occurrence.id != original.id
    assert occurrence.due_date == date(2026, 10, 14)
    assert occurrence.description == original.description


def test_weekly_recurrence_advances_seven_days() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(make_task("weekly-1", "Groom", date(2026, 10, 13), "15:00", "weekly"))

    Scheduler(owner).mark_task_complete("weekly-1")

    assert pet.tasks[1].due_date == date(2026, 10, 20)
    assert pet.tasks[1].completed is False


def test_completing_task_twice_creates_no_duplicate_recurrence() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(make_task("daily-1", "Walk", date(2026, 10, 13), frequency="daily"))
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete("daily-1")
    scheduler.mark_task_complete("daily-1")

    assert len(pet.tasks) == 2
    assert [task.id for task in pet.tasks].count("daily-1") == 1


def test_one_time_task_creates_no_new_task() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(make_task("once-1", "Feed", date(2026, 10, 13)))

    Scheduler(owner).mark_task_complete("once-1")

    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


def test_daily_recurrence_crosses_month_and_year_boundary() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(make_task("new-year", "Walk", date(2026, 12, 31), frequency="daily"))

    Scheduler(owner).mark_task_complete("new-year")

    assert pet.tasks[1].due_date == date(2027, 1, 1)


def test_same_date_and_time_conflict_across_pets() -> None:
    owner, first_pet, second_pet, scheduler = make_owner_with_pets()
    conflict_date = date(2026, 10, 13)
    first_pet.add_task(make_task("dog-task", "Dog walk", conflict_date, "09:00"))
    second_pet.add_task(make_task("cat-task", "Cat feeding", conflict_date, "09:00"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Mochi" in warnings[0]
    assert "Luna" in warnings[0]
    assert "09:00" in warnings[0]


def test_same_time_on_different_dates_has_no_conflict() -> None:
    owner, first_pet, second_pet, scheduler = make_owner_with_pets()
    first_pet.add_task(make_task("dog-task", "Dog walk", date(2026, 10, 13), "09:00"))
    second_pet.add_task(make_task("cat-task", "Cat feeding", date(2026, 10, 14), "09:00"))

    assert scheduler.detect_conflicts() == []


def test_completed_tasks_do_not_cause_active_conflicts() -> None:
    owner, first_pet, second_pet, scheduler = make_owner_with_pets()
    conflict_date = date(2026, 10, 13)
    first_pet.add_task(make_task("dog-task", "Dog walk", conflict_date, "09:00", completed=True))
    second_pet.add_task(make_task("cat-task", "Cat feeding", conflict_date, "09:00"))

    assert scheduler.detect_conflicts() == []


def test_empty_owner_and_pet_have_no_tasks() -> None:
    owner = Owner("Jordan", 60)
    empty_pet = Pet("pet-1", "Mochi", "dog")

    assert owner.get_all_tasks() == []
    assert empty_pet.tasks == []
    assert Scheduler(owner).sort_by_time() == []
    assert Scheduler(owner).detect_conflicts() == []


@pytest.mark.parametrize("invalid_time", ["8:00", "08:0", "24:00", "12:60", "noon"])
def test_invalid_task_times_are_rejected(invalid_time: str) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        make_task("bad-time", "Walk", date(2026, 10, 13), invalid_time)


@pytest.mark.parametrize("duration", [0, -1])
def test_nonpositive_durations_are_rejected(duration: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        make_task("bad-duration", "Walk", date(2026, 10, 13), duration=duration)


def test_editing_preserves_task_identity_and_validates_changes() -> None:
    pet = Pet("pet-1", "Mochi", "dog")
    original = make_task("original-id", "Old walk", date(2026, 10, 13))
    pet.add_task(original)
    updated = make_task("different-id", "New walk", date(2026, 10, 14), "10:00", duration=15)

    pet.edit_task("original-id", updated)

    assert pet.tasks[0].id == "original-id"
    assert pet.tasks[0].description == "New walk"
    assert pet.tasks[0].due_date == date(2026, 10, 14)
    with pytest.raises(ValueError, match="positive"):
        make_task("invalid-edit", "Invalid", date(2026, 10, 13), duration=0)


def test_daily_plan_respects_priority_date_completion_and_budget() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    plan_date = date(2026, 10, 13)
    pet.add_task(make_task("high", "High priority", plan_date, "10:00", priority="high", duration=5))
    pet.add_task(make_task("medium", "Medium priority", plan_date, "08:00", priority="medium", duration=10))
    pet.add_task(make_task("completed", "Already done", plan_date, completed=True, duration=1))
    pet.add_task(make_task("future", "Future task", plan_date + timedelta(days=1), duration=1))

    selected, skipped = Scheduler(owner).generate_daily_plan(plan_date, available_minutes=10)

    assert [task.id for task in selected] == ["high"]
    assert [task.id for task in skipped] == ["medium"]
    assert sum(task.duration_minutes for task in selected) <= 10
    assert "completed" not in [task.id for task in selected]
    assert "future" not in [task.id for task in selected]


def test_daily_plan_skips_long_task_and_considers_shorter_task() -> None:
    owner = Owner("Jordan", 60)
    pet = Pet("pet-1", "Mochi", "dog")
    owner.add_pet(pet)
    plan_date = date(2026, 10, 13)
    pet.add_task(make_task("too-long", "Long walk", plan_date, "08:00", priority="high", duration=20))
    pet.add_task(make_task("short", "Short walk", plan_date, "09:00", priority="medium", duration=5))

    selected, skipped = Scheduler(owner).generate_daily_plan(plan_date, available_minutes=5)

    assert [task.id for task in selected] == ["short"]
    assert [task.id for task in skipped] == ["too-long"]