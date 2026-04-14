from __future__ import annotations

from typing import Any

from app.models.question import Question


class QuizSession:
    def __init__(
        self,
        questions: list[Question],
        player_name: str = "Player",
        current_index: int = 0,
        score: int = 0,
        answers: list[str] | None = None,
        settings: dict[str, Any] | None = None,
        status: str = "in_progress",
    ) -> None:
        self._questions = list(questions)
        self._player_name = player_name
        self._current_index = current_index
        self._score = score
        self._answers = list(answers or [])
        self._settings = dict(settings or {})
        self._status = status

    @property
    def player_name(self) -> str:
        return self._player_name

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def score(self) -> int:
        return self._score

    @property
    def total_questions(self) -> int:
        return len(self._questions)

    @property
    def answers(self) -> list[str]:
        return list(self._answers)

    @property
    def settings(self) -> dict[str, Any]:
        return dict(self._settings)

    def is_finished(self) -> bool:
        return self._current_index >= len(self._questions)

    def current_question(self) -> Question | None:
        if self.is_finished():
            return None
        return self._questions[self._current_index]

    def submit_answer(self, answer: str) -> bool:
        question = self.current_question()
        if question is None:
            raise ValueError("quiz session is already finished")

        is_correct = question.is_correct(answer)
        self._answers.append(answer)
        if is_correct:
            self._score += 1
        return is_correct

    def next_question(self) -> bool:
        if self.is_finished():
            self._status = "finished"
            return False

        self._current_index += 1
        if self.is_finished():
            self._status = "finished"
            return False

        self._status = "in_progress"
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_name": self._player_name,
            "current_index": self._current_index,
            "score": self._score,
            "question_order": [question.id for question in self._questions],
            "answers": list(self._answers),
            "settings": dict(self._settings),
            "status": "finished" if self.is_finished() else self._status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], questions: list[Question]) -> "QuizSession":
        question_map = {question.id: question for question in questions}
        order = list(data.get("question_order", []))

        ordered_questions: list[Question] = []
        for question_id in order:
            if question_id not in question_map:
                raise ValueError(f"question id not found: {question_id}")
            ordered_questions.append(question_map[question_id])

        return cls(
            questions=ordered_questions,
            player_name=str(data.get("player_name", "Player")),
            current_index=int(data.get("current_index", 0)),
            score=int(data.get("score", 0)),
            answers=list(data.get("answers", [])),
            settings=dict(data.get("settings", {})),
            status=str(data.get("status", "in_progress")),
        )
