from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from app.models.question import Question


class QuestionBank:
    def __init__(self, questions: list[Question] | None = None) -> None:
        self._questions: list[Question] = list(questions or [])

    @property
    def questions(self) -> list[Question]:
        return list(self._questions)

    @classmethod
    def from_json(cls, json_path: str | Path = "data/questions.json") -> "QuestionBank":
        path = Path(json_path)
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("questions json must be a list")

        questions = [Question.from_dict(item) for item in data]
        return cls(questions)

    def save_json(self, json_path: str | Path = "data/questions.json") -> None:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2)

    def delete_by_index(self, index: int) -> Question:
        if index < 1 or index > len(self._questions):
            raise ValueError("삭제할 퀴즈 번호가 범위를 벗어났습니다.")
        return self._questions.pop(index - 1)

    def filter_by_difficulty(self, difficulty: str) -> "QuestionBank":
        filtered = [q for q in self._questions if q.difficulty == difficulty]
        return QuestionBank(filtered)

    def shuffled(self, seed: int | None = None) -> "QuestionBank":
        shuffled_questions = list(self._questions)
        rng = random.Random(seed)
        rng.shuffle(shuffled_questions)
        return QuestionBank(shuffled_questions)

    def to_dict(self) -> list[dict[str, Any]]:
        return [question.to_dict() for question in self._questions]
