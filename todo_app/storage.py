"""Read and write task data in JSON format."""

import json
import os
import tempfile
from pathlib import Path

from .models import Task


class StorageError(Exception):
    """Raised when task data cannot safely be read or written."""


class JsonTaskStorage:
    """Load and save tasks in a local JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> list[Task]:
        """Load saved tasks. A missing file means the list is empty."""
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                content = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(
                f"Could not read task data from '{self.file_path}': {exc}"
            ) from exc

        if not isinstance(content, list):
            raise StorageError("The task data file must contain a JSON list.")

        tasks: list[Task] = []
        seen_ids: set[int] = set()
        for index, record in enumerate(content, start=1):
            try:
                task = Task.from_dict(record)
            except ValueError as exc:
                raise StorageError(f"Invalid task record at item {index}: {exc}") from exc

            if task.task_id in seen_ids:
                raise StorageError(f"Duplicate task ID found: {task.task_id}.")
            seen_ids.add(task.task_id)
            tasks.append(task)

        return tasks

    def save(self, tasks: list[Task]) -> None:
        """Write to a temporary file before replacing the saved task file."""
        temporary_path: Path | None = None
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    [task.to_dict() for task in tasks],
                    temporary_file,
                    indent=4,
                    ensure_ascii=False,
                )
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            # Keeping the temporary file in the same folder allows an atomic replace.
            os.replace(temporary_path, self.file_path)
            temporary_path = None
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Could not save task data to '{self.file_path}': {exc}"
            ) from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
