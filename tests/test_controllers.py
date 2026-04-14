import json
import tempfile
import unittest
from pathlib import Path

from app.controllers.app_controller import AppController
from app.controllers.game_controller import GameController
from app.models.question import Question
from app.models.quiz_session import QuizSession


class DummyGameView:
    def __init__(self, selections):
        self._selections = list(selections)
        self.errors = []
        self.messages = []
        self.final_score = None

    def show_question(self, question_text, index, total):
        return None

    def show_choices(self, choices):
        return None

    def prompt_choice(self, choice_count):
        return self._selections.pop(0)

    def show_answer_result(self, is_correct):
        return None

    def show_final_score(self, score, total):
        self.final_score = (score, total)

    def show_message(self, message):
        self.messages.append(message)

    def show_error(self, message):
        self.errors.append(message)


class DummyMenuView:
    def __init__(self):
        self.errors = []
        self.messages = []

    def show_main_menu(self):
        return None

    def prompt_main_menu_choice(self):
        return 3

    def prompt_save_on_exit(self):
        return False

    def show_message(self, message):
        self.messages.append(message)

    def show_error(self, message):
        self.errors.append(message)


class TestControllers(unittest.TestCase):
    def test_game_controller_runs_and_accumulates_score(self):
        q1 = Question(1, "Q1", ["A", "B"], "A", "easy")
        q2 = Question(2, "Q2", ["A", "B"], "B", "easy")
        session = QuizSession([q1, q2])

        saved_scores = []

        def on_progress(current_session):
            saved_scores.append(current_session.score)

        view = DummyGameView([1, 2])
        controller = GameController(session, game_view=view, on_progress=on_progress)

        completed = controller.run()

        self.assertTrue(completed)
        self.assertEqual(session.score, 2)
        self.assertEqual(view.final_score, (2, 2))
        self.assertGreaterEqual(len(saved_scores), 2)

    def test_app_controller_load_game_without_state_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            questions_file = tmp / "questions.json"
            questions_file.write_text(
                json.dumps(
                    [
                        {
                            "id": 1,
                            "text": "Q1",
                            "choices": ["A", "B"],
                            "answer": "A",
                            "difficulty": "easy",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            menu_view = DummyMenuView()
            app_controller = AppController(
                menu_view=menu_view,
                questions_path=questions_file,
                state_path=tmp / "missing_state.json",
            )

            app_controller._load_game()
            self.assertIn("저장된 게임이 없습니다.", menu_view.errors)


if __name__ == "__main__":
    unittest.main()
