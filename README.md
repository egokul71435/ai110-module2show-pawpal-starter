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

## Smarter Scheduling

Beyond basic priority sorting, the scheduler includes three additional features:

- **Recurring tasks** — Tasks with a `daily` or `weekly` frequency automatically generate their next occurrence when marked complete, using `timedelta` to calculate the correct due date. One-time tasks simply close out.
- **Conflict detection** — After a schedule is built (or manually constructed), `detect_conflicts()` checks every pair of entries for overlapping time ranges and returns human-readable warnings rather than crashing.
- **Filtering** — `filter_tasks()` lets you narrow tasks by completion status, pet name, or both, making it easy to answer questions like "what does Whiskers still need today?"

The core algorithm is a greedy fit: tasks are sorted by priority then duration, and each task is added to the plan if it fits in the owner's remaining time. This keeps the logic simple and the reasoning text explainable at the cost of occasionally leaving small time gaps that a knapsack approach could fill.

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
