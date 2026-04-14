import tempfile
import unittest
from pathlib import Path

from app.models.state_repository import StateRepository


class TestStateRepository(unittest.TestCase):
    def test_save_and_load_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            repo = StateRepository(state_file)

            state = {
                "player_name": "kim",
                "current_index": 1,
                "score": 2,
                "question_order": [3, 1, 2],
                "answers": ["A", "B"],
                "settings": {"difficulty": "easy"},
                "status": "in_progress",
            }

            repo.save(state)
            loaded = repo.load()
            self.assertEqual(loaded, state)

    def test_corrupted_state_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            state_file.write_text("{ invalid json", encoding="utf-8")
            repo = StateRepository(state_file)

            with self.assertRaises(ValueError):
                repo.load()


if __name__ == "__main__":
    unittest.main()
