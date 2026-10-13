# PawPal+

PawPal+ is a Streamlit pet-care planning app. It stores an owner's pets and their care tasks, then helps organize tasks by date, time, priority, and available care minutes.

## Implemented Features

- Created an owner with an available-minute budget.
- Added multiple pets, including pets with duplicate names.
- Add tasks with descriptions, dates, zero-padded times, durations, priorities, and once/daily/weekly frequencies.
- Validate names, descriptions, durations, priorities, frequencies, and times.
- Edit incomplete tasks while preserving their IDs.
- Sort and filter tasks across all pets.
- Complete tasks and create the next occurrence for recurring tasks.
- Detect exact same-date, same-time conflicts across pets.
- Generate a greedy daily plan with selected and skipped tasks.
- Use Streamlit session state for session-only data storage.

## Setup on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation for the current terminal, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## Run PawPal+

Run the reproducible CLI demo:

```powershell
python main.py
```

Run the Streamlit app:

```powershell
python -m streamlit run app.py
```

Run the tests:

```powershell
python -m pytest
```

## How the Classes Work Together

`Owner` stores the owner settings and a list of `Pet` objects. Each `Pet` stores its own `Task` objects. `Owner.get_all_tasks()` provides `(pet, task)` pairs across every pet. `Scheduler` receives the owner and uses that aggregation for sorting, filtering, recurrence, conflict detection, and daily planning. `Task` validates its own data and tracks completion.

## Smarter Scheduling

| Feature | Actual method | Behavior |
|---|---|---|
| Task sorting | `Scheduler.sort_by_time()` | Orders all tasks by due date and then time without changing pet task lists. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet ID, completion status, and due date. |
| Recurrence | `Scheduler.mark_task_complete()` | Completes the original task and creates one daily or weekly occurrence with a new ID. |
| Conflict handling | `Scheduler.detect_conflicts()` | Reports incomplete tasks with the same exact date and start time, including across pets. |
| Time-budget planning | `Scheduler.generate_daily_plan()` | Considers high, medium, then low priority tasks, skips tasks that do not fit, and returns selected and skipped lists. |

The conflict check compares exact start times; it does not calculate overlapping durations. The daily plan uses a greedy strategy, so it is not guaranteed to find the globally optimal combination of tasks.

## Demo Walkthrough

1. Open the Streamlit app and enter the owner's name and available care minutes.
2. Add two pets, such as Mochi and Luna. Pets are tracked by unique IDs internally, so duplicate names would remain separate.
3. Add tasks to either pet with descriptions, dates, times, durations, priorities, and frequencies.
4. Review the chronological schedule and use the pet, completion-status, and date filters.
5. When two incomplete tasks share a date and exact start time, review the warning displayed by the app.
6. Select an incomplete task, edit its fields, and save the changes. Its task ID is preserved.
7. Complete a daily or weekly task. The original becomes complete and its next occurrence appears as a new incomplete task.
8. Choose a plan date and generate a daily plan. The app shows selected tasks, skipped tasks, the available-minute budget, and the selection explanation.

## Sample Output

This is the captured output from `python main.py`:

```text
Chronological sorting:
  08:00 - Breakfast (10 min, medium, incomplete, 2026-10-13)
  09:00 - Morning walk (20 min, high, incomplete, 2026-10-13)
  09:00 - Medication (5 min, high, incomplete, 2026-10-13)
  11:00 - Grooming (25 min, low, incomplete, 2026-10-13)

Filters:
  Luna tasks: Breakfast, Medication
  Incomplete tasks: Morning walk, Grooming, Breakfast, Medication

Conflicts:
  Conflict on 2026-10-13 at 09:00: Mochi - Morning walk; Luna - Medication.

Daily recurrence:
  Mochi: 09:00 - Morning walk (20 min, high, complete, 2026-10-13)
  Mochi: 11:00 - Grooming (25 min, low, incomplete, 2026-10-13)
  Mochi: 09:00 - Morning walk (20 min, high, incomplete, 2026-10-14)

Time-budget plan (35 minutes):
  Selection rule: high priority first, then medium and low, then time; selected tasks are shown chronologically.
  Selected:
    Breakfast (10 min)
    Medication (5 min)
  Skipped because they exceed the remaining budget:
    Grooming (25 min)
```

## Testing PawPal+

Run the full suite with:

```powershell
python -m pytest
```

Captured result:

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\slakh\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 24 items                                                              

tests\test_pawpal.py ........................                            [100%]

============================= 24 passed in 0.06s ==============================
```

The tests cover the original task completion and task-addition behaviors, chronological sorting, aggregation across two pets, all filters, daily and weekly recurrence, duplicate completion, one-time tasks, date-boundary recurrence, conflicts and conflict exclusions, empty collections, validation errors, identity-preserving edits, and priority-aware daily planning under a time budget.

## Diagrams

- [UML draft](diagrams/uml_draft.mmd)
- [UML final](diagrams/uml_final.mmd)

## Limitations

- Data is stored in Streamlit `session_state` only. It remains available during the current session but is not permanent storage.
- Conflict detection checks exact start times only and does not detect duration overlaps.
- Daily planning is greedy: it prioritizes tasks and skips tasks that do not fit, but it is not globally optimal.