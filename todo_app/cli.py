"""Command-line menu and user interaction."""

from pathlib import Path

from .manager import TaskManager
from .storage import JsonTaskStorage, StorageError


MENU = """\nTO-DO LIST MANAGER
1. Add a task
2. View all tasks
3. Mark a task as completed
4. Remove a task
5. Exit
"""


def main() -> None:
    """Start the menu and keep running until the user chooses to exit."""
    # Keep the task file beside the project rather than depending on the terminal folder.
    project_folder = Path(__file__).resolve().parent.parent
    storage = JsonTaskStorage(project_folder / "data" / "tasks.json")

    try:
        manager = TaskManager(storage)
    except StorageError as exc:
        print(f"Unable to load saved tasks: {exc}")
        return

    print("Welcome! Manage your tasks using the menu below.")

    while True:
        print(MENU)

        try:
            choice = input("Choose an option (1-5): ").strip()
            if choice == "1":
                add_task(manager)
            elif choice == "2":
                view_tasks(manager)
            elif choice == "3":
                complete_task(manager)
            elif choice == "4":
                remove_task(manager)
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Please choose a number from 1 to 5.")
        except StorageError as exc:
            print(f"Could not save your changes: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nApplication closed.")
            break


def add_task(manager: TaskManager) -> None:
    """Ask for a title and add it to the list."""
    title = input("Enter task title: ")
    try:
        task = manager.add_task(title)
        print(f"Task added with ID {task.task_id}.")
    except ValueError as exc:
        print(f"Invalid task: {exc}")


def view_tasks(manager: TaskManager) -> None:
    """Display every task and its current status."""
    tasks = manager.list_tasks()
    if not tasks:
        print("Your task list is empty.")
        return

    print("\nYour tasks:")
    for task in tasks:
        status = "Completed" if task.completed else "Pending"
        print(f"[{task.task_id}] {task.title} - {status}")


def complete_task(manager: TaskManager) -> None:
    """Read an ID and mark the matching task as completed."""
    task_id = read_task_id()
    if task_id is None:
        return
    if manager.mark_completed(task_id):
        print(f"Task {task_id} marked as completed.")
    else:
        print(f"No task found with ID {task_id}.")


def remove_task(manager: TaskManager) -> None:
    """Read an ID and remove the matching task."""
    task_id = read_task_id()
    if task_id is None:
        return
    if manager.remove_task(task_id):
        print(f"Task {task_id} removed.")
    else:
        print(f"No task found with ID {task_id}.")


def read_task_id() -> int | None:
    """Read and validate a positive numeric ID from the user."""
    value = input("Enter task ID: ").strip()
    try:
        task_id = int(value)
        if task_id < 1:
            raise ValueError
        return task_id
    except ValueError:
        print("Please enter a positive whole-number ID.")
        return None
