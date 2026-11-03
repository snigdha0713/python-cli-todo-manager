"""Tests for task creation and task-management operations."""

import tempfile
import unittest
from pathlib import Path

from todo_app.manager import TaskManager
from todo_app.storage import JsonTaskStorage


class TaskManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        file_path = Path(self.temp_dir.name) / "tasks.json"
        self.manager = TaskManager(JsonTaskStorage(file_path))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_task_trims_title_and_assigns_id(self) -> None:
        task = self.manager.add_task("  Submit assignment  ")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.title, "Submit assignment")
        self.assertFalse(task.completed)

    def test_empty_title_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_title_over_100_characters_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.add_task("x" * 101)

    def test_mark_completed_changes_status(self) -> None:
        task = self.manager.add_task("Revise Python")
        self.assertTrue(self.manager.mark_completed(task.task_id))
        self.assertTrue(self.manager.list_tasks()[0].completed)

    def test_mark_completed_returns_false_for_unknown_id(self) -> None:
        self.assertFalse(self.manager.mark_completed(999))

    def test_remove_task(self) -> None:
        task = self.manager.add_task("Buy notebooks")
        self.assertTrue(self.manager.remove_task(task.task_id))
        self.assertEqual(self.manager.list_tasks(), [])
        self.assertFalse(self.manager.remove_task(task.task_id))

    def test_next_id_does_not_reuse_deleted_id(self) -> None:
        first = self.manager.add_task("First")
        self.manager.add_task("Second")
        self.manager.remove_task(first.task_id)
        third = self.manager.add_task("Third")
        self.assertEqual(third.task_id, 3)

    def test_tasks_survive_application_restart(self) -> None:
        self.manager.add_task("Saved task")
        storage = self.manager._storage
        reopened_manager = TaskManager(storage)
        self.assertEqual(reopened_manager.list_tasks()[0].title, "Saved task")

    def test_invalid_task_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.remove_task(0)


if __name__ == "__main__":
    unittest.main()
