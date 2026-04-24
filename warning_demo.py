#!/usr/bin/env python3
"""
Lightweight Warning System Demo for Pawlpal Ultra
Shows how the time-based scheduling features provide fast warning messages
"""

from pawpal_system import Schedule, Owner, Pet, Task, Priority, Frequency, ScheduleWarning
from datetime import time as datetime_time

def demo_lightweight_warnings():
    print("🐾 Pawlpal Ultra Lightweight Warning System Demo")
    print("=" * 50)

    # Create a schedule with some issues
    schedule = Schedule()
    owner = Owner("Demo Owner", 30, "123 Demo St")

    # Create pets
    fluffy = Pet("Fluffy", "Cat", 3, "Female")
    spot = Pet("Spot", "Dog", 5, "Male")
    owner.add_pet(fluffy)
    owner.add_pet(spot)

    # Add tasks without scheduling them (will create warnings)
    feeding = Task("Feeding", 10, Priority.HIGH, frequency=Frequency.DAILY)
    walking = Task("Walking", 30, Priority.MEDIUM, frequency=Frequency.DAILY)
    grooming = Task("Grooming", 45, Priority.LOW, frequency=Frequency.WEEKLY)

    fluffy.add_task(feeding)
    spot.add_task(walking)
    fluffy.add_task(grooming)

    schedule.add_task(feeding)
    schedule.add_task(walking)
    schedule.add_task(grooming)

    print("\n1️⃣ UNSCHEDULED TASKS WARNING:")
    warnings = schedule.get_warnings()
    for warning in warnings:
        print(f"   {warning.severity.upper()}: {warning.message}")

    print("\n2️⃣ QUICK CONFLICT CHECK:")
    has_conflicts = schedule.has_conflicts()
    print(f"   Has conflicts: {'❌ YES' if has_conflicts else '✅ NO'}")

    print("\n3️⃣ ASSIGN TIMES (returns warnings):")
    assignment_warnings = schedule.assign_start_times(8, 0)
    for warning in assignment_warnings:
        print(f"   {warning.severity.upper()}: {warning.message}")

    print("\n4️⃣ CONFLICT SUMMARY ONLY:")
    conflict_summary = schedule.get_conflict_summary()
    if conflict_summary:
        print(conflict_summary)
    else:
        print("   ✅ No conflicts!")

    print("\n5️⃣ CREATE OVERLAPS MANUALLY:")
    # Create overlapping times
    schedule.tasks[0].start_time = datetime_time(9, 0)   # 9:00-9:10
    schedule.tasks[1].start_time = datetime_time(9, 5)   # 9:05-9:35 (overlaps!)
    schedule.tasks[2].start_time = datetime_time(10, 0)  # 10:00-10:45

    warnings = schedule.get_warnings()
    conflict_warnings = [w for w in warnings if w.severity in ['error', 'warning']]
    print(f"   Created {len(conflict_warnings)} conflicts:")
    for warning in conflict_warnings:
        print(f"   {warning.severity.upper()}: {warning.message}")

    print("\n6️⃣ RESOLVE OVERLAPS (lightweight):")
    success, resolution_warnings = schedule.resolve_overlaps()
    print(f"   Resolution: {'✅ SUCCESS' if success else '❌ FAILED'}")
    for warning in resolution_warnings:
        if warning.severity in ['error', 'warning']:
            print(f"   {warning.severity.upper()}: {warning.message}")

    print("\n7️⃣ FINAL VALIDATION:")
    validation_warnings = schedule.validate_schedule()
    critical_issues = [w for w in validation_warnings if w.severity == 'error']
    warnings_list = [w for w in validation_warnings if w.severity == 'warning']

    if not validation_warnings:
        print("   ✅ Schedule is perfect!")
    else:
        print(f"   🚨 {len(critical_issues)} errors, {len(warnings_list)} warnings")
        for warning in validation_warnings:
            print(f"   {warning.severity.upper()}: {warning.message}")

    print("\n8️⃣ PERFORMANCE TEST:")
    import time
    start = time.time()
    for _ in range(1000):
        schedule.get_warnings()
        schedule.has_conflicts()
        schedule.get_conflict_summary()
    end = time.time()
    print(".4f")

if __name__ == "__main__":
    demo_lightweight_warnings()