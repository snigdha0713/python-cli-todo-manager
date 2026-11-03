"""Data models used by the To-Do List application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Task:
    """One task stored by the application.

    Tasks are immutable so that changes are made explicitly through TaskManager.
    This helps keep the in-memory list and the saved JSON file in sync.
    """

    task_id: int
    title: str
    completed: bool = False
    created_at: str = ""

    @classmethod
    def create(cls, task_id: int, title: str) -> "Task":
        """Create a new task with a local ISO-8601 creation timestamp."""
        return cls(
            task_id=task_id,
            title=title,
            completed=False,
            created_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the task to a JSON-serializable dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "Task":
        """Build a task from stored data, rejecting malformed records."""
        if not isinstance(data, dict):
            raise ValueError("each task must be a JSON object")

        task_id = data.get("task_id")
        title = data.get("title")
        completed = data.get("completed")
        created_at = data.get("created_at")

        # bool is a subclass of int in Python, so use an exact type check for IDs.
        if type(task_id) is not int or task_id < 1:
            raise ValueError("task_id must be a positive integer")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        if type(completed) is not bool:
            raise ValueError("completed must be true or false")
        if not isinstance(created_at, str) or not created_at.strip():
            raise ValueError("created_at must be a non-empty string")

        return cls(
            task_id=task_id,
            title=title,
            completed=completed,
            created_at=created_at,
        )
