from dataclasses import dataclass, field, replace
from datetime import date, timedelta
import re
from uuid import uuid4


ALLOWED_FREQUENCIES = {"once", "daily", "weekly"}
ALLOWED_PRIORITIES = {"high", "medium", "low"}
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


@dataclass
class Task:
    """A care task for a pet."""

    id: str
    description: str
    due_date: date
    time: str
    frequency: str
    completed: bool = False
    duration_minutes: int = 0
    priority: str = "medium"

    def __post_init__(self) -> None:
        """Validate task details."""
        if not self.id.strip():
            raise ValueError("Task ID must not be empty.")
        if not self.description.strip():
            raise ValueError("Task description must not be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be positive.")
        if self.frequency not in ALLOWED_FREQUENCIES:
            raise ValueError("Frequency must be once, daily, or weekly.")
        if self.priority not in ALLOWED_PRIORITIES:
            raise ValueError("Priority must be high, medium, or low.")
        if not TIME_PATTERN.fullmatch(self.time):
            raise ValueError("Task time must use zero-padded HH:MM format.")

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True


@dataclass
class Pet:
    """A pet and its care tasks."""

    id: str
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate pet details."""
        if not self.id.strip():
            raise ValueError("Pet ID must not be empty.")
        if not self.name.strip():
            raise ValueError("Pet name must not be empty.")
        if not self.species.strip():
            raise ValueError("Pet species must not be empty.")

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def edit_task(self, task_id: str, updated_task: Task) -> None:
        """Update a task belonging to this pet."""
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks[index] = replace(updated_task, id=task_id)
                return
        raise ValueError(f"Task '{task_id}' was not found for {self.name}.")


class Owner:
    """An owner with available time and pets."""

    def __init__(self, name: str, available_minutes: int) -> None:
        if not name.strip():
            raise ValueError("Owner name must not be empty.")
        if available_minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return each pet and its tasks as pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Plan tasks for an owner."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        """Return all tasks ordered by due date and time."""
        pairs = self.owner.get_all_tasks()
        return [task for _, task in sorted(pairs, key=lambda pair: (pair[1].due_date, pair[1].time))]

    def filter_tasks(
        self,
        pet_id: str | None = None,
        completed: bool | None = None,
        due_date: date | None = None,
    ) -> list[Task]:
        """Return tasks matching the requested filters."""
        pairs = self.owner.get_all_tasks()
        return [
            task
            for pet, task in pairs
            if (pet_id is None or pet.id == pet_id)
            and (completed is None or task.completed == completed)
            and (due_date is None or task.due_date == due_date)
        ]

    def mark_task_complete(self, task_id: str) -> None:
        """Complete a task and schedule its next recurrence."""
        for pet, task in self.owner.get_all_tasks():
            if task.id == task_id:
                if task.completed:
                    return
                task.mark_complete()
                if task.frequency != "once":
                    days_to_add = 1 if task.frequency == "daily" else 7
                    pet.add_task(
                        replace(
                            task,
                            id=f"{task.id}-{uuid4().hex[:8]}",
                            due_date=task.due_date + timedelta(days=days_to_add),
                            completed=False,
                        )
                    )
                return
        raise ValueError(f"Task '{task_id}' was not found.")

    def detect_conflicts(self) -> list[str]:
        """Warn about exact start-time matches, not overlapping durations."""
        pairs = [pair for pair in self.owner.get_all_tasks() if not pair[1].completed]
        warnings: list[str] = []
        for index, (first_pet, first_task) in enumerate(pairs):
            for second_pet, second_task in pairs[index + 1 :]:
                same_start = (
                    first_task.due_date == second_task.due_date
                    and first_task.time == second_task.time
                )
                if same_start:
                    warnings.append(
                        f"Conflict on {first_task.due_date} at {first_task.time}: "
                        f"{first_pet.name} - {first_task.description}; "
                        f"{second_pet.name} - {second_task.description}."
                    )
        return warnings

    def generate_daily_plan(
        self, plan_date: date, available_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        """Select a priority-aware plan and return selected and skipped tasks."""
        if available_minutes < 0:
            raise ValueError("Available minutes cannot be negative.")

        priority_order = {"high": 0, "medium": 1, "low": 2}
        candidates = [
            task
            for _, task in self.owner.get_all_tasks()
            if task.due_date == plan_date and not task.completed
        ]
        candidates.sort(key=lambda task: (priority_order[task.priority], task.time))

        selected: list[Task] = []
        skipped: list[Task] = []
        remaining_minutes = available_minutes
        for task in candidates:
            if task.duration_minutes <= remaining_minutes:
                selected.append(task)
                remaining_minutes -= task.duration_minutes
            else:
                skipped.append(task)

        selected.sort(key=lambda task: task.time)
        return selected, skipped