from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Question:
    id: int
    text: str
    choices: list[str]
    answer: str
    difficulty: str

    def __post_init__(self) -> None:
        if len(self.choices) < 2:
            raise ValueError("choices must contain at least 2 items")
        if self.answer not in self.choices:
            raise ValueError("answer must be one of choices")

    def is_correct(self, selected_answer: str) -> bool:
        return selected_answer == self.answer

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "choices": list(self.choices),
            "answer": self.answer,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question":
        return cls(
            id=int(data["id"]),
            text=str(data["text"]),
            choices=list(data["choices"]),
            answer=str(data["answer"]),
            difficulty=str(data["difficulty"]),
        )
