"""Command-line interface and application entry point."""

from pathlib import Path

from .manager import TaskManager
from .storage import JsonTaskStorage, StorageError


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def _read_task_id(prompt: str) -> int | None:
    """Read a positive task ID, returning None for invalid input."""
    raw_value = input(prompt).strip()
    try:
        task_id = int(raw_value)
    except ValueError:
        print("Please enter a whole-number task ID, such as 1.")
        return None

    if task_id < 1:
        print("Task ID must be greater than zero.")
        return None
    return task_id


def _show_tasks(manager: TaskManager) -> None:
    tasks = manager.list_tasks()
    if not tasks:
        print("\nYour task list is empty. Add a task to get started.\n")
        return

    print("\nYOUR TASKS")
    print("-" * 60)
    for task in tasks:
        status = "✓ Completed" if task.completed else "○ Pending"
        print(f"[{task.task_id}] {task.title}  |  {status}")
    print("-" * 60)
    print(f"Total: {len(tasks)} task(s)\n")


def _handle_add(manager: TaskManager) -> None:
    title = input("Enter task title: ")
    try:
        task = manager.add_task(title)
        print(f"Added task [{task.task_id}]: {task.title}\n")
    except ValueError as exc:
        print(f"Invalid task: {exc}\n")
    except StorageError as exc:
        print(f"Could not save the task. Your list was not changed.\nDetails: {exc}\n")


def _handle_complete(manager: TaskManager) -> None:
    task_id = _read_task_id("Enter the task ID to mark as completed: ")
    if task_id is None:
        return
    try:
        if manager.mark_completed(task_id):
            print(f"Task [{task_id}] marked as completed.\n")
        else:
            print(f"No task found with ID {task_id}.\n")
    except (ValueError, StorageError) as exc:
        print(f"Could not complete the task: {exc}\n")


def _handle_remove(manager: TaskManager) -> None:
    task_id = _read_task_id("Enter the task ID to remove: ")
    if task_id is None:
        return
    try:
        if manager.remove_task(task_id):
            print(f"Task [{task_id}] removed.\n")
        else:
            print(f"No task found with ID {task_id}.\n")
    except (ValueError, StorageError) as exc:
        print(f"Could not remove the task: {exc}\n")


def run_cli(manager: TaskManager) -> None:
    """Display the menu until the user chooses to exit."""
    print("\nWELCOME TO THE TO-DO LIST MANAGER")

    while True:
        print("1. Add a task")
        print("2. View all tasks")
        print("3. Mark a task as completed")
        print("4. Remove a task")
        print("5. Exit")

        try:
            choice = input("Choose an option (1-5): ").strip()
            if choice == "1":
                _handle_add(manager)
            elif choice == "2":
                _show_tasks(manager)
            elif choice == "3":
                _handle_complete(manager)
            elif choice == "4":
                _handle_remove(manager)
            elif choice == "5":
                print("Your tasks are saved. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 5.\n")
        except (EOFError, KeyboardInterrupt):
            # Treat Ctrl+D / Ctrl+Z and Ctrl+C as a clean exit instead of a traceback.
            print("\nInput interrupted. Your saved tasks are safe. Goodbye!")
            break


def main() -> int:
    """Create the application objects and start the CLI."""
    try:
        manager = TaskManager(JsonTaskStorage(DATA_FILE))
    except StorageError as exc:
        print(f"Unable to start because the saved task data could not be loaded.\n{exc}")
        print("Your saved file has not been overwritten. Check or repair it, then try again.")
        return 1

    run_cli(manager)
    return 0
