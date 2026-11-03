"""Tests for JSON task storage and corrupted-file handling."""

import tempfile
import unittest
from pathlib import Path

from todo_app.models import Task
from todo_app.storage import JsonTaskStorage, StorageError


class JsonTaskStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tasks.json"
        self.storage = JsonTaskStorage(self.file_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self) -> None:
        self.assertEqual(self.storage.load(), [])

    def test_save_and_load_round_trip(self) -> None:
        expected = [Task.create(1, "Read a chapter")]
        self.storage.save(expected)
        self.assertEqual(self.storage.load(), expected)

    def test_invalid_json_raises_storage_error(self) -> None:
        self.file_path.write_text("{not valid JSON", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.storage.load()

    def test_wrong_top_level_type_raises_storage_error(self) -> None:
        self.file_path.write_text('{"task_id": 1}', encoding="utf-8")
        with self.assertRaises(StorageError):
            self.storage.load()

    def test_duplicate_ids_raise_storage_error(self) -> None:
        task = Task.create(1, "Repeated ID")
        self.storage.save([task, task])
        with self.assertRaises(StorageError):
            self.storage.load()


if __name__ == "__main__":
    unittest.main()
