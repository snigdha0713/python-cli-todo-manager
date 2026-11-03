"""Task operations and validation rules."""

from .models import Task
from .storage import JsonTaskStorage


class TaskManager:
    """Manage the task list independently of the command-line interface."""

    MAX_TITLE_LENGTH = 100

    def __init__(self, storage: JsonTaskStorage) -> None:
        self._storage = storage
        self._tasks = storage.load()

    def list_tasks(self) -> list[Task]:
        """Return a copy so callers cannot change the internal list directly."""
        return list(self._tasks)

    def add_task(self, title: str) -> Task:
        """Validate and add a task, saving it before changing in-memory data."""
        if not isinstance(title, str):
            raise ValueError("Task title must be text.")

        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if len(clean_title) > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"Task title cannot be longer than {self.MAX_TITLE_LENGTH} characters."
            )

        # Use the highest existing ID so removing a task does not reuse its ID.
        next_id = max((task.task_id for task in self._tasks), default=0) + 1
        task = Task.create(next_id, clean_title)
        self._save_before_update([*self._tasks, task])
        return task

    def mark_completed(self, task_id: int) -> bool:
        """Mark a matching task as completed. Return False when it is not found."""
        self._validate_id(task_id)
        for index, task in enumerate(self._tasks):
            if task.task_id == task_id:
                if task.completed:
                    return True
                updated = list(self._tasks)
                updated[index] = Task(
                    task_id=task.task_id,
                    title=task.title,
                    completed=True,
                    created_at=task.created_at,
                )
                self._save_before_update(updated)
                return True
        return False

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by ID. Return False when no matching task exists."""
        self._validate_id(task_id)
        updated = [task for task in self._tasks if task.task_id != task_id]
        if len(updated) == len(self._tasks):
            return False
        self._save_before_update(updated)
        return True

    @staticmethod
    def _validate_id(task_id: int) -> None:
        # bool values should not be accepted as numeric task IDs.
        if type(task_id) is not int or task_id < 1:
            raise ValueError("Task ID must be a positive whole number.")

    def _save_before_update(self, updated_tasks: list[Task]) -> None:
        """Persist first, then update memory only when saving succeeds."""
        self._storage.save(updated_tasks)
        self._tasks = updated_tasks
