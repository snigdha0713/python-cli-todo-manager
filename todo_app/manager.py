"""Application logic for adding, listing, completing, and removing tasks."""

from .models import Task
from .storage import JsonTaskStorage


class TaskManager:
    """Coordinate task operations and persist each successful change."""

    MAX_TITLE_LENGTH = 100

    def __init__(self, storage: JsonTaskStorage) -> None:
        self._storage = storage
        self._tasks = storage.load()

    def list_tasks(self) -> list[Task]:
        """Return a copy so callers cannot modify the manager's internal list."""
        return list(self._tasks)

    def add_task(self, title: str) -> Task:
        """Validate and add a task. Returns the newly created task."""
        if not isinstance(title, str):
            raise ValueError("Task title must be text.")

        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if len(clean_title) > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"Task title must be {self.MAX_TITLE_LENGTH} characters or fewer."
            )

        # IDs are generated from the largest existing ID, not the list length,
        # so deleting a task does not accidentally reuse an existing ID.
        next_id = max((task.task_id for task in self._tasks), default=0) + 1
        new_task = Task.create(next_id, clean_title)
        updated_tasks = [*self._tasks, new_task]
        self._save_before_update(updated_tasks)
        return new_task

    def mark_completed(self, task_id: int) -> bool:
        """Mark a task as completed. Returns False when the ID is not found."""
        self._validate_task_id(task_id)
        if not any(task.task_id == task_id for task in self._tasks):
            return False

        updated_tasks = [
            Task(task.task_id, task.title, True, task.created_at)
            if task.task_id == task_id
            else task
            for task in self._tasks
        ]
        self._save_before_update(updated_tasks)
        return True

    def remove_task(self, task_id: int) -> bool:
        """Remove a task. Returns False when the ID is not found."""
        self._validate_task_id(task_id)
        updated_tasks = [task for task in self._tasks if task.task_id != task_id]
        if len(updated_tasks) == len(self._tasks):
            return False

        self._save_before_update(updated_tasks)
        return True

    @staticmethod
    def _validate_task_id(task_id: int) -> None:
        # Reject bool because True and False otherwise behave like 1 and 0.
        if type(task_id) is not int or task_id < 1:
            raise ValueError("Task ID must be a positive whole number.")

    def _save_before_update(self, updated_tasks: list[Task]) -> None:
        """Persist first; update memory only after the save succeeds."""
        self._storage.save(updated_tasks)
        self._tasks = updated_tasks
