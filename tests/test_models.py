import json
import tempfile
import unittest
from pathlib import Path

from app.models.question import Question
from app.models.question_bank import QuestionBank
from app.models.quiz_session import QuizSession


class TestModels(unittest.TestCase):
    def test_question_bank_loading_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            valid_file = tmp_path / "questions.json"
            valid_file.write_text(
                json.dumps(
                    [
                        {
                            "id": 1,
                            "text": "2+2?",
                            "choices": ["3", "4"],
                            "answer": "4",
                            "difficulty": "easy",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            bank = QuestionBank.from_json(valid_file)
            self.assertEqual(len(bank.questions), 1)
            self.assertEqual(bank.questions[0].text, "2+2?")

            invalid_file = tmp_path / "invalid.json"
            invalid_file.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                QuestionBank.from_json(invalid_file)

    def test_answer_check_and_score_accumulation(self):
        q1 = Question(1, "2+2?", ["3", "4"], "4", "easy")
        q2 = Question(2, "3+3?", ["5", "6"], "6", "easy")
        session = QuizSession([q1, q2])

        self.assertTrue(q1.is_correct("4"))
        self.assertFalse(q1.is_correct("3"))

        self.assertTrue(session.submit_answer("4"))
        session.next_question()
        self.assertFalse(session.submit_answer("5"))

        self.assertEqual(session.score, 1)
        self.assertEqual(session.answers, ["4", "5"])

    def test_session_serialization_and_restore(self):
        q1 = Question(1, "A?", ["a", "b"], "a", "easy")
        q2 = Question(2, "B?", ["c", "d"], "d", "medium")

        session = QuizSession([q2, q1], player_name="kim", settings={"difficulty": "all"})
        session.submit_answer("d")
        session.next_question()

        data = session.to_dict()

        restored = QuizSession.from_dict(data, [q1, q2])
        self.assertEqual(restored.player_name, "kim")
        self.assertEqual(restored.current_index, 1)
        self.assertEqual(restored.score, 1)
        self.assertEqual(restored.answers, ["d"])

        current = restored.current_question()
        self.assertIsNotNone(current)
        self.assertEqual(current.id, 1)


if __name__ == "__main__":
    unittest.main()
