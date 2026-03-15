# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Demo

<a href="/course_images/ai110/demo.png" target="_blank"><img src='/course_images/ai110/demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

The screenshot shows the filtering panel, the generated schedule with priority sorting and reasoning text, and the time-budget summary banner.

## Features

### Scheduling engine
- **Priority-based greedy scheduling** — Tasks are sorted by priority (high → medium → low), with shorter tasks first as a tiebreaker. The scheduler greedily fills the owner's available time window, skipping tasks that don't fit. Each scheduled task includes a plain-English reasoning line explaining why it was placed where it is.
- **Chronological sorting** — `sort_by_time()` reorders schedule entries by their `HH:MM` start time using a lambda key that splits the string into an `(hour, minute)` tuple for correct numeric comparison.
- **Time-budget enforcement** — The owner's `available_minutes` acts as a hard ceiling. Tasks are added until the budget is exhausted; remaining tasks are reported in the summary but not scheduled.

### Task lifecycle
- **Daily and weekly recurrence** — When a recurring task is marked complete, `mark_complete()` uses `timedelta` to calculate the next due date (+1 day for daily, +7 days for weekly) and returns a fresh incomplete copy. One-time tasks return `None` and simply close out.
- **Completion tracking** — Each task carries a `completed` flag. `Pet.complete_task()` marks the task done and auto-appends the next occurrence to the pet's task list in a single call.

### Safety and filtering
- **Conflict detection** — `detect_conflicts()` compares every pair of schedule entries using `itertools.combinations` and the standard interval-overlap test (`a_start < b_end AND b_start < a_end`). Overlapping entries produce human-readable warnings displayed as `st.warning` banners in the UI rather than crashing.
- **Task filtering** — `filter_tasks()` narrows the full task list by completion status, pet name, or both. Results are displayed in a filterable table in the Streamlit UI.

### User interface
- **Session state persistence** — Owner, pets, tasks, and the generated schedule survive across Streamlit reruns using `st.session_state` with guard checks (`"key" not in st.session_state`).
- **Interactive task completion** — Checkbox widgets per task trigger `complete_task()`, with an `st.success` toast showing the next due date for recurring tasks.
- **Stale schedule clearing** — Adding a pet, adding a task, or toggling completion automatically invalidates the cached schedule so the user always sees up-to-date results.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite contains **15 tests** across five categories:

| Category | Tests | What they verify |
|----------|-------|-----------------|
| Basic operations | 2 | Task completion status toggle, task count after adding to a pet |
| Sorting correctness | 3 | Priority ordering (high → low), duration tiebreaker, chronological `sort_by_time()` |
| Recurrence logic | 4 | Daily task → +1 day, weekly → +7 days, one-time → no recurrence, Pet auto-appends next occurrence |
| Conflict detection | 3 | Overlapping time ranges flagged, adjacent (non-overlapping) entries pass clean, identical start times flagged |
| Edge cases | 3 | Pet with no tasks → empty schedule, zero available minutes → nothing scheduled, all tasks completed → empty schedule |

**Confidence level: 4/5**

The test suite covers all core scheduling behaviors, recurrence rules, and boundary conditions. One star is withheld because the tests do not yet cover multi-pet cross-schedule interactions or UI-level integration with Streamlit session state — areas that could harbor bugs not caught by unit tests alone.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
