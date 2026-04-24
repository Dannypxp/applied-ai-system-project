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


### Algorithm Features

PawPal+ implements several sophisticated algorithms for intelligent pet care scheduling:

#### 1. **Priority-Based Sorting (`create_plan()`)**
- **Algorithm**: O(n log n) sorting using Python's `sorted()` with custom key function
- **Logic**: Tasks sorted by priority (HIGH → MEDIUM → LOW) then by duration (shortest first)
- **Use Case**: Creates optimized daily plans prioritizing important tasks while considering efficiency

#### 2. **Duration-Based Sorting (`sort_by_duration()`)**
- **Algorithm**: O(n log n) sorting by duration in ascending order
- **Logic**: Uses `sorted()` with `key=lambda t: t.duration_minutes`
- **Use Case**: Alternative sorting for efficiency-focused scheduling

#### 3. **Task Filtering (`filter_tasks()`)**
- **Algorithm**: O(n) linear search with conditional filtering
- **Logic**: Filters tasks by completion status and/or pet name
- **Use Case**: View specific subsets (e.g., incomplete tasks for a particular pet)

#### 4. **Sequential Time Assignment (`assign_start_times()`)**
- **Algorithm**: O(n) sequential assignment with time arithmetic
- **Logic**: Assigns start times incrementally starting from 8:00 AM, adding duration + 5-minute buffer
- **Use Case**: Automatically schedules tasks in logical sequence with proper spacing

#### 5. **Overlap Detection (`detect_overlaps()` & `_tasks_overlap()`)**
- **Algorithm**: O(n²) pairwise comparison using triangular matrix approach (i < j)
- **Logic**: Converts times to minutes-since-midnight, checks interval overlap: `start1 < end2 AND start2 < end1`
- **Features**: Handles overnight tasks, unscheduled tasks, and different conflict types (same-pet vs owner-capacity)
- **Use Case**: Identifies scheduling conflicts before they cause problems

#### 6. **Conflict Resolution (`resolve_overlaps()`)**
- **Algorithm**: Automated sequential reassignment strategy
- **Logic**: Reassigns all start times sequentially, then verifies conflicts remain
- **Use Case**: Automatic conflict resolution when manual scheduling becomes complex

#### 7. **Schedule Validation & Warnings (`get_warnings()`, `has_conflicts()`, `get_conflict_summary()`)**
- **Algorithm**: Multi-pass validation with O(n²) overlap detection
- **Logic**: Checks unscheduled tasks, time overlaps, and overnight tasks
- **Features**: Color-coded severity levels (error/warning/info) with detailed messages
- **Use Case**: Comprehensive schedule validation for UI feedback and automated systems

#### 8. **Recurring Task Management (`_create_next_recurring_task()`)**
- **Algorithm**: Factory method pattern for task creation
- **Logic**: Automatically creates next occurrence for DAILY/WEEKLY tasks when completed
- **Features**: Maintains referential integrity by adding to both schedule and pet's task list
- **Use Case**: Handles recurring care tasks without manual recreation

#### 9. **Time Calculation (`end_time` property in Task)**
- **Algorithm**: Arithmetic time calculation with modulo for next-day handling
- **Logic**: Converts to minutes, adds duration, handles wraparound past midnight
- **Use Case**: Automatic end time calculation for overlap detection and display

#### 10. **Data Validation (`__post_init__` in Task)**
- **Algorithm**: Constructor validation
- **Logic**: Ensures duration > 0, raises ValueError if invalid
- **Use Case**: Prevents invalid task creation at runtime

### Performance Characteristics
- **Sorting Operations**: O(n log n) - efficient for typical schedule sizes
- **Filtering/Searching**: O(n) - linear time for real-time filtering
- **Overlap Detection**: O(n²) - acceptable for small schedules (<100 tasks)
- **Time Assignment**: O(n) - fast sequential processing
- **Validation**: O(n²) due to overlap checks - optimized with early filtering

### Key Edge Cases Handled
- Overnight tasks spanning midnight
- Unscheduled vs scheduled tasks
- Same-pet vs different-pet conflicts
- Invalid durations and times
- Recurring task chains
- Empty schedules and single tasks


### 3 core variables to test
1. creating owener
2. creating multiple pets under 1 owner
3. sorting tasks based on pet
4. generating a plan for the day
5.catch overlapping tasks


### Testing Pawpal+

python -m pytest

The tests goes over sorting by duration and priority, task reaccurance, conflict detection

Ill give my reliability a 4/5 because all the tests past from pytest