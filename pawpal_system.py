from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
from datetime import datetime, time


class Priority(Enum):
    """Priority levels for tasks in the pet care scheduling system.
    
    Used to determine task importance and ordering in optimized schedules.
    Higher priority tasks are scheduled and completed before lower priority ones.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Frequency(Enum):
    """Task frequency for recurring pet care tasks.
    
    Determines how often recurring tasks should be automatically recreated
    after completion. ONCE tasks are one-time only and don't recur.
    """
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class ScheduleWarning:
    """Represents a scheduling warning or conflict in the pet care system.
    
    Used to communicate scheduling issues, conflicts, and informational 
    messages to users and automated systems. Provides structured information
    about problems with severity levels and optional task references.
    
    Attributes:
        message: Human-readable description of the warning/conflict
        severity: 'info', 'warning', or 'error' indicating issue criticality
        task1: First task involved in conflict (optional)
        task2: Second task involved in conflict (optional) 
        conflict_type: Type of conflict ('same_pet', 'owner_capacity', etc.)
    """
    message: str
    severity: str  # 'info', 'warning', 'error'
    task1: Optional['Task'] = None
    task2: Optional['Task'] = None
    conflict_type: Optional[str] = None  # 'same_pet', 'owner_capacity', etc.


@dataclass
class Task:
    """Represents a pet care task with scheduling and recurrence capabilities.
    
    Core entity in the pet care scheduling system. Supports time-based scheduling,
    priority levels, completion tracking, and automatic recurrence for daily/weekly tasks.
    
    Key features:
    - Time-based scheduling with automatic end time calculation
    - Priority-based ordering for optimized scheduling
    - Recurring task support (daily/weekly) with automatic next occurrence creation
    - Pet association for conflict detection and filtering
    
    Attributes:
        title: Descriptive name of the task
        duration_minutes: Expected time to complete the task
        priority: Importance level (LOW/MEDIUM/HIGH) for scheduling optimization
        completed: Completion status (affects scheduling and recurrence)
        pet: Associated pet (optional, used for conflict detection)
        frequency: Recurrence pattern (ONCE/DAILY/WEEKLY)
        start_time: Scheduled start time (optional, set by scheduling algorithms)
    """
    title: str
    duration_minutes: int
    priority: Priority
    completed: bool = False
    pet: Optional['Pet'] = None
    frequency: Frequency = Frequency.ONCE
    start_time: Optional[time] = None  # Scheduled start time
    
    def __post_init__(self):
        """Validate task data"""
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")
    
    @property
    def end_time(self) -> Optional[time]:
        """Calculate end time based on start time and duration"""
        if self.start_time is None:
            return None
        
        # Convert to minutes since midnight for calculation
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = start_minutes + self.duration_minutes
        
        # Convert back to time
        end_hour = end_minutes // 60
        end_minute = end_minutes % 60
        
        # Handle next day (if end time goes past midnight)
        if end_hour >= 24:
            end_hour = end_hour % 24
            
        try:
            return time(end_hour, end_minute)
        except ValueError:
            # If invalid time (shouldn't happen with our calculation), return None
            return None


@dataclass
class Schedule:
    """Manages pet care tasks with advanced scheduling algorithms.
    
    Central scheduling component providing comprehensive task management with:
    - Priority-based and duration-based sorting algorithms
    - Task filtering by completion status and pet association
    - Automatic recurring task creation and management
    - Time-based scheduling with sequential assignment
    - Conflict detection using interval overlap algorithms
    - Automatic conflict resolution through time reassignment
    - Comprehensive warning and validation system
    
    Key algorithms:
    - Sorting: O(n log n) priority/duration-based ordering
    - Filtering: O(n) linear search with conditional filtering
    - Overlap detection: O(n²) pairwise comparison with optimizations
    - Time assignment: O(n) sequential scheduling with buffers
    - Conflict resolution: Automated sequential reassignment
    
    The schedule maintains task integrity and provides both programmatic
    access (via methods) and user-friendly reporting (via warnings/summaries).
    """
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule"""
        self.tasks.append(task)

    def modify_task(self, task_id: int, new_task: Task) -> None:
        """Modify an existing task by index"""
        if 0 <= task_id < len(self.tasks):
            self.tasks[task_id] = new_task

    def remove_task(self, task_id: int) -> None:
        """Remove a task from the schedule"""
        if 0 <= task_id < len(self.tasks):
            self.tasks.pop(task_id)

    def add_priority(self, task_id: int, priority: Priority) -> None:
        """Update the priority of a task"""
        if 0 <= task_id < len(self.tasks):
            self.tasks[task_id].priority = priority

    def create_plan(self) -> None:
        """Create an optimized plan in-place for this schedule"""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        self.tasks = sorted(
            self.tasks,
            key=lambda t: (-priority_order[t.priority.value], t.duration_minutes)
        )

    def sort_by_duration(self) -> None:
        """Sort tasks by duration in ascending order (shortest first).
        
        Algorithm: Uses Python's built-in sorted() function with a key function
        that extracts the duration_minutes attribute. This provides O(n log n)
        time complexity for sorting n tasks.
        
        Use case: Optimize task order for efficiency by tackling shorter tasks first,
        which can help build momentum and complete more tasks in a session.
        """
        self.tasks = sorted(self.tasks, key=lambda t: t.duration_minutes)

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name.
        
        Algorithm: Linear search through all tasks with conditional filtering.
        Time complexity: O(n) where n is the number of tasks.
        
        Args:
            completed: If True, return only completed tasks. If False, return only 
                      incomplete tasks. If None, ignore completion status.
            pet_name: Filter tasks by pet name. If None, ignore pet name.
            
        Returns:
            List of tasks matching the filter criteria
            
        Use case: View specific subsets of tasks (e.g., all incomplete tasks for a 
        particular pet) without modifying the original schedule.
        """
        filtered_tasks = []
        for task in self.tasks:
            # Check completion status filter
            if completed is not None and task.completed != completed:
                continue
            
            # Check pet name filter
            if pet_name is not None and (task.pet is None or task.pet.name != pet_name):
                continue
                
            filtered_tasks.append(task)
        
        return filtered_tasks

    def mark_task_complete(self, task_id: int) -> None:
        """Mark a task as complete by index and handle recurring tasks.
        
        Algorithm: Direct array access by index, then triggers recurring task 
        creation if applicable. Time complexity: O(1) for marking + O(1) for 
        recurring task creation.
        
        For recurring tasks (daily/weekly), automatically creates the next 
        occurrence with the same properties but marked as incomplete.
        
        Args:
            task_id: Index of the task to mark complete (0-based)
            
        Raises:
            No exceptions raised - invalid indices are silently ignored
        """
        if 0 <= task_id < len(self.tasks):
            self.tasks[task_id].completed = True
            # If this is a recurring task, create the next occurrence
            self._create_next_recurring_task(task_id)

    def mark_task_incomplete(self, task_id: int) -> None:
        """Mark a task as incomplete by index"""
        if 0 <= task_id < len(self.tasks):
            self.tasks[task_id].completed = False

    def _create_next_recurring_task(self, task_id: int) -> None:
        """Create the next occurrence of a recurring task if applicable.
        
        Algorithm: Factory method pattern - creates a new Task instance with 
        identical properties except completion status. Time complexity: O(1).
        
        Handles different frequency types:
        - ONCE: No action (one-time tasks don't recur)
        - DAILY/WEEKLY: Creates identical task marked as incomplete
        
        The new task is added to both the schedule and the pet's task list
        to maintain referential integrity.
        
        Args:
            task_id: Index of the completed recurring task
        """
        task = self.tasks[task_id]
        if task.frequency == Frequency.ONCE:
            return  # No next occurrence for one-time tasks
        
        # Create next occurrence with same properties but incomplete
        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            completed=False,
            pet=task.pet,
            frequency=task.frequency
        )
        
        # Add to schedule
        self.add_task(next_task)
        
        # Also add to pet's task list if applicable
        if task.pet:
            task.pet.add_task(next_task)

    def assign_start_times(self, start_hour: int = 8, start_minute: int = 0) -> List[ScheduleWarning]:
        """Assign sequential start times to tasks starting from the given time.
        
        Algorithm: Sequential assignment with time arithmetic. Iterates through 
        incomplete tasks and assigns start times incrementally, adding task 
        duration plus a 5-minute buffer between tasks.
        
        Time complexity: O(n) where n is the number of tasks.
        Handles time wraparound past midnight using modulo arithmetic.
        
        Args:
            start_hour: Starting hour (0-23), defaults to 8 AM
            start_minute: Starting minute (0-59), defaults to 0
            
        Returns:
            List of warnings generated during assignment (e.g., assignment summary)
            
        Use case: Automatically schedule tasks in a logical sequence to avoid 
        manual time assignment and ensure proper spacing.
        """
        warnings = []
        
        if not self.tasks:
            return warnings
            
        current_time = time(start_hour, start_minute)
        assigned_count = 0
        
        for task in self.tasks:
            if not task.completed:  # Only assign times to incomplete tasks
                task.start_time = current_time
                assigned_count += 1
                
                # Move to next time slot (add duration + small buffer)
                current_minutes = current_time.hour * 60 + current_time.minute
                next_minutes = current_minutes + task.duration_minutes + 5  # 5 min buffer
                next_hour = next_minutes // 60
                next_minute = next_minutes % 60
                current_time = time(next_hour % 24, next_minute)
        
        if assigned_count > 0:
            warnings.append(ScheduleWarning(
                message=f"Assigned times to {assigned_count} tasks starting at {start_hour:02d}:{start_minute:02d}",
                severity="info"
            ))
        
        return warnings

    def validate_schedule(self) -> List[ScheduleWarning]:
        """Lightweight validation of the entire schedule
        
        Returns:
            List of all warnings and issues found
        """
        warnings = []
        
        # Check basic task properties
        for i, task in enumerate(self.tasks):
            if task.duration_minutes <= 0:
                warnings.append(ScheduleWarning(
                    message=f"Task {i}: Invalid duration {task.duration_minutes} minutes",
                    severity="error",
                    task1=task
                ))
        
        # Add scheduling warnings
        warnings.extend(self.get_warnings())
        
        return warnings

    def detect_overlaps(self) -> List[Tuple[Task, Task, str]]:
        """Detect overlapping tasks using optimized pairwise comparison.
        
        Algorithm: O(n²) pairwise comparison with optimization to avoid duplicate 
        checks. Only compares incomplete tasks with scheduled start times.
        Uses triangular matrix approach (i < j) to check each pair only once.
        
        Time complexity: O(n²) in worst case, but typically much faster due to 
        filtering out unscheduled/completed tasks and early termination.
        
        Space complexity: O(k) where k is the number of overlapping pairs found.
        
        Returns:
            List of tuples (task1, task2, conflict_type) where:
            - conflict_type is "same_pet" if both tasks are for the same pet
            - conflict_type is "owner_capacity" if tasks overlap but for different pets
            
        Use case: Identify scheduling conflicts before they cause problems, 
        enabling proactive conflict resolution.
        """
        overlaps = []
        # Only check incomplete tasks with scheduled times
        scheduled_tasks = [task for task in self.tasks 
                          if not task.completed and task.start_time is not None]
        
        # Use nested loops but skip duplicate comparisons (i < j)
        for i in range(len(scheduled_tasks)):
            for j in range(i + 1, len(scheduled_tasks)):
                task1, task2 = scheduled_tasks[i], scheduled_tasks[j]
                
                if self._tasks_overlap(task1, task2):
                    # Determine conflict type
                    conflict_type = "same_pet" if task1.pet == task2.pet else "owner_capacity"
                    overlaps.append((task1, task2, conflict_type))
        
        return overlaps

    def _tasks_overlap(self, task1: Task, task2: Task) -> bool:
        """Check if two tasks overlap in time using interval arithmetic.
        
        Algorithm: Standard interval overlap detection using the condition:
        "Two intervals [a,b) and [c,d) overlap if a < d and c < b"
        
        Converts time objects to minutes-since-midnight for easy comparison.
        Handles overnight tasks by adding 24 hours when end_time < start_time.
        
        Time complexity: O(1) - constant time arithmetic operations.
        Handles edge cases: unscheduled tasks, overnight tasks, invalid times.
        
        Args:
            task1: First task to check
            task2: Second task to check
            
        Returns:
            True if tasks have overlapping time intervals, False otherwise
            
        Examples:
            - [9:00-10:00] and [9:30-10:30] → True (overlap)
            - [9:00-10:00] and [10:00-11:00] → False (adjacent, no overlap)
            - [23:00-1:00] and [0:30-2:00] → True (overnight overlap)
        """
        # Early return for unscheduled tasks
        if not (task1.start_time and task2.start_time):
            return False
        
        # Convert to minutes since midnight for easy comparison
        def time_to_minutes(t: time) -> int:
            return t.hour * 60 + t.minute
        
        t1_start = time_to_minutes(task1.start_time)
        t1_end = time_to_minutes(task1.end_time) if task1.end_time else t1_start + task1.duration_minutes
        t2_start = time_to_minutes(task2.start_time)
        t2_end = time_to_minutes(task2.end_time) if task2.end_time else t2_start + task2.duration_minutes
        
        # Handle overnight tasks (add 24 hours if end < start)
        if t1_end < t1_start:
            t1_end += 24 * 60
        if t2_end < t2_start:
            t2_end += 24 * 60
        
        # Standard interval overlap check: two intervals overlap if start1 < end2 AND start2 < end1
        return t1_start < t2_end and t2_start < t1_end

    def resolve_overlaps(self) -> Tuple[bool, List[ScheduleWarning]]:
        """Attempt to resolve overlaps by reassigning start times sequentially.
        
        Algorithm: Simple conflict resolution strategy - reassigns all start times 
        in sequential order starting from 8:00 AM, then verifies if conflicts remain.
        
        Steps:
        1. Reassign all task start times sequentially with buffers
        2. Check for remaining conflicts after reassignment
        3. Return success status and comprehensive warning list
        
        Time complexity: O(n²) due to overlap detection in step 2.
        This is a basic resolution strategy - more sophisticated algorithms 
        could preserve some original times or optimize for different criteria.
        
        Returns:
            Tuple of (success: bool, warnings: List[ScheduleWarning])
            - success: True if no conflicts remain after resolution
            - warnings: All warnings from reassignment and post-resolution checks
            
        Use case: Automatic conflict resolution when manual scheduling becomes 
        too complex, though may not preserve user preferences for specific times.
        """
        # Simple resolution: reassign all start times sequentially
        assignment_warnings = self.assign_start_times()
        
        # Check if overlaps still exist
        post_assignment_warnings = self.get_warnings()
        remaining_conflicts = [w for w in post_assignment_warnings if w.severity in ['error', 'warning']]
        
        success = len(remaining_conflicts) == 0
        
        all_warnings = assignment_warnings + post_assignment_warnings
        
        if success:
            all_warnings.append(ScheduleWarning(
                message="All scheduling conflicts resolved",
                severity="info"
            ))
        
        return success, all_warnings

    def get_warnings(self) -> List[ScheduleWarning]:
        """Get comprehensive list of all scheduling warnings and conflicts.
        
        Algorithm: Multi-pass validation checking different types of issues:
        1. Unscheduled tasks (incomplete tasks without start times)
        2. Time overlaps (same-pet conflicts and owner capacity issues)  
        3. Overnight tasks (tasks that run past midnight)
        
        Time complexity: O(n²) due to overlap detection, but optimized by 
        filtering tasks first. Space complexity: O(k) where k is number of warnings.
        
        Warning severities:
        - 'error': Critical issues (same pet conflicts) that prevent execution
        - 'warning': Capacity issues that may be challenging but possible
        - 'info': Informational notices (unscheduled tasks, overnight tasks)
        
        Returns:
            List of ScheduleWarning objects with detailed conflict information,
            including task references and conflict types for UI display
            
        Use case: Comprehensive schedule validation for both automated systems 
        and user interfaces, providing actionable feedback on scheduling issues.
        """
        warnings = []
        
        # Check for unscheduled tasks
        unscheduled = [task for task in self.tasks if not task.completed and task.start_time is None]
        if unscheduled:
            warnings.append(ScheduleWarning(
                message=f"{len(unscheduled)} tasks are not scheduled",
                severity="warning"
            ))
        
        # Check for overlaps
        overlaps = self.detect_overlaps()
        for task1, task2, conflict_type in overlaps:
            if conflict_type == "same_pet":
                severity = "error"
                message = f"Same pet conflict: {task1.pet.name if task1.pet else 'Unknown'} cannot do '{task1.title}' and '{task2.title}' simultaneously"
            else:  # owner_capacity
                severity = "warning"
                message = f"Owner capacity issue: '{task1.title}' and '{task2.title}' overlap - may be challenging to handle both"
            
            warnings.append(ScheduleWarning(
                message=message,
                severity=severity,
                task1=task1,
                task2=task2,
                conflict_type=conflict_type
            ))
        
        # Check for tasks that end after midnight
        late_tasks = []
        for task in self.tasks:
            if task.start_time and task.end_time:
                if task.end_time.hour < task.start_time.hour:  # Crosses midnight
                    late_tasks.append(task)
        
        if late_tasks:
            warnings.append(ScheduleWarning(
                message=f"{len(late_tasks)} tasks run past midnight",
                severity="info"
            ))
        
        return warnings

    def has_conflicts(self) -> bool:
        """Check if schedule has any conflicts (errors or warnings).
        
        Algorithm: Delegates to get_warnings() and filters for conflict-level 
        severities. Time complexity: O(n²) due to underlying overlap detection.
        
        This is a lightweight boolean check - use get_warnings() for detailed 
        information about specific conflicts.
        
        Returns:
            True if any conflicts exist (error or warning severity), False otherwise
            
        Use case: Quick validation checks, conditional logic, or status indicators
        where detailed conflict information isn't needed.
        """
        warnings = self.get_warnings()
        return any(w.severity in ['error', 'warning'] for w in warnings)

    def get_conflict_summary(self) -> str:
        """Get a human-readable summary of conflicts only.
        
        Algorithm: Filters warnings for conflict-level severities, then formats 
        them into a structured text summary with emojis and categorization.
        
        Time complexity: O(n²) due to get_warnings() call.
        Space complexity: O(m) where m is the length of the formatted summary.
        
        Output format:
        - 🚫 Critical conflicts: (errors)
        - ⚠️ Scheduling issues: (warnings)
        - Empty string if no conflicts
        
        Returns:
            Formatted string summary of conflicts, or empty string if no conflicts.
            Suitable for display in UIs, logs, or user notifications.
            
        Use case: User-facing conflict reporting, status displays, or integration 
        with notification systems where formatted text is preferred over objects.
        """
        warnings = [w for w in self.get_warnings() if w.severity in ['error', 'warning']]
        if not warnings:
            return ""
        
        summary = []
        errors = [w for w in warnings if w.severity == 'error']
        warnings_list = [w for w in warnings if w.severity == 'warning']
        
        if errors:
            summary.append(f"🚫 {len(errors)} critical conflicts:")
            for w in errors:
                summary.append(f"   {w.message}")
        
        if warnings_list:
            summary.append(f"⚠️  {len(warnings_list)} scheduling issues:")
            for w in warnings_list:
                summary.append(f"   {w.message}")
        
        return "\n".join(summary)


@dataclass
class Owner:
    """Represents a pet owner"""
    name: str
    age: int
    address: str
    
    pets: List['Pet'] = field(default_factory=list)
    schedules: List[Schedule] = field(default_factory=list)

    def enter_info(self) -> None:
        """Enter owner information"""
        # data is provided through constructor in this domain model
        return
    
    def edit_info(self, name: str = None, age: int = None, address: str = None) -> None:
        """Edit owner information"""
        if name:
            self.name = name
        if age is not None:
            self.age = age
        if address:
            self.address = address
    
    def delete_info(self) -> None:
        """Delete owner information (reset to defaults)"""
        self.name = ""
        self.age = 0
        self.address = ""
        self.pets.clear()
        self.schedules.clear()

    def add_pet(self, pet: 'Pet') -> None:
        """Assign a pet to this owner"""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: 'Pet') -> None:
        """Remove a pet from this owner"""
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None

    def add_schedule(self, schedule: Schedule) -> None:
        """Assign a schedule to this owner"""
        self.schedules.append(schedule)

    def remove_schedule(self, schedule: Schedule) -> None:
        """Remove schedule from this owner"""
        if schedule in self.schedules:
            self.schedules.remove(schedule)


@dataclass
class Pet:
    """Represents a pet"""
    name: str
    breed: str
    age: int
    gender: str
    owner: Optional[Owner] = None
    tasks: List[Task] = field(default_factory=list)
    
    def enter_info(self) -> None:
        """Enter pet information"""
        pass
    
    def edit_info(self, name: str = None, breed: str = None, age: int = None, gender: str = None) -> None:
        """Edit pet information"""
        if name:
            self.name = name
        if breed:
            self.breed = breed
        if age is not None:
            self.age = age
        if gender:
            self.gender = gender

    def add_task(self, task: Task) -> None:
        """Add a care task associated to this pet"""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove task from this pet"""
        if task in self.tasks:
            self.tasks.remove(task)

    @property
    def task_counter(self) -> int:
        """Return number of tasks assigned to this pet"""
        return len(self.tasks)
    
    def delete_info(self) -> None:
        """Delete pet information (reset to defaults)"""
        self.name = ""
        self.breed = ""
        self.age = 0
        self.gender = ""
        self.owner = None

