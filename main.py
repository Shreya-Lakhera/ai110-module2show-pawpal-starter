from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


DEMO_DATE = date(2026, 10, 13)


def describe(task: Task) -> str:
    """Return readable task details."""
    status = "complete" if task.completed else "incomplete"
    return (
        f"{task.time} - {task.description} ({task.duration_minutes} min, "
        f"{task.priority}, {status}, {task.due_date})"
    )


def main() -> None:
    """Run a reproducible PawPal+ backend demonstration."""
    owner = Owner("Jordan", available_minutes=35)
    mochi = Pet("pet-1", "Mochi", "dog")
    luna = Pet("pet-2", "Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("task-1", "Morning walk", DEMO_DATE, "09:00", "daily", duration_minutes=20, priority="high"))
    luna.add_task(Task("task-2", "Breakfast", DEMO_DATE, "08:00", "once", duration_minutes=10, priority="medium"))
    luna.add_task(Task("task-3", "Medication", DEMO_DATE, "09:00", "once", duration_minutes=5, priority="high"))
    mochi.add_task(Task("task-4", "Grooming", DEMO_DATE, "11:00", "once", duration_minutes=25, priority="low"))

    scheduler = Scheduler(owner)

    print("Chronological sorting:")
    for task in scheduler.sort_by_time():
        print(f"  {describe(task)}")

    print("\nFilters:")
    print("  Luna tasks:", ", ".join(task.description for task in scheduler.filter_tasks(pet_id="pet-2")))
    print(
        "  Incomplete tasks:",
        ", ".join(task.description for task in scheduler.filter_tasks(completed=False)),
    )

    print("\nConflicts:")
    for warning in scheduler.detect_conflicts():
        print(f"  {warning}")

    scheduler.mark_task_complete("task-1")
    print("\nDaily recurrence:")
    for task in mochi.tasks:
        print(f"  Mochi: {describe(task)}")

    selected, skipped = scheduler.generate_daily_plan(DEMO_DATE, available_minutes=35)
    print("\nTime-budget plan (35 minutes):")
    print("  Selection rule: high priority first, then medium and low, then time; selected tasks are shown chronologically.")
    print("  Selected:")
    for task in selected:
        print(f"    {task.description} ({task.duration_minutes} min)")
    print("  Skipped because they exceed the remaining budget:")
    for task in skipped:
        print(f"    {task.description} ({task.duration_minutes} min)")


if __name__ == "__main__":
    main()