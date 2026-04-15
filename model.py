from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class QuizQuestion:
    id: int
    question: str
    choices: list[str]
    answer: int
    hint: Optional[str] = None

    def is_valid(self) -> bool:
        return (
            isinstance(self.id, int)
            and isinstance(self.question, str)
            and self.question.strip() != ""
            and isinstance(self.choices, list)
            and len(self.choices) == 4
            and all(isinstance(choice, str) and choice.strip() != "" for choice in self.choices)
            and isinstance(self.answer, int)
            and 1 <= self.answer <= 4
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QuizQuestion":
        return cls(
            id=data["id"],
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint"),
        )


@dataclass
class GameState:
    in_progress: bool = False
    question_ids: list[int] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0
    answers: list[dict] = field(default_factory=list)
    options: dict = field(default_factory=dict)

    def start_new(self, question_ids: list[int], options: dict) -> None:
        self.in_progress = True
        self.question_ids = question_ids
        self.current_index = 0
        self.correct_count = 0
        self.answers = []
        self.options = options

    def record_answer(self, question_id: int, selected: int, correct: bool) -> None:
        self.answers.append(
            {
                "question_id": question_id,
                "selected": selected,
                "correct": correct,
            }
        )
        if correct:
            self.correct_count += 1
        self.current_index += 1

    def is_finished(self) -> bool:
        return self.in_progress and self.current_index >= len(self.question_ids)

    def clear(self) -> None:
        self.in_progress = False
        self.question_ids = []
        self.current_index = 0
        self.correct_count = 0
        self.answers = []
        self.options = {}

    def to_dict(self) -> dict:
        return {
            "in_progress": self.in_progress,
            "question_ids": self.question_ids,
            "current_index": self.current_index,
            "correct_count": self.correct_count,
            "answers": self.answers,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        return cls(
            in_progress=data.get("in_progress", False),
            question_ids=data.get("question_ids", []),
            current_index=data.get("current_index", 0),
            correct_count=data.get("correct_count", 0),
            answers=data.get("answers", []),
            options=data.get("options", {}),
        )


class QuestionBank:
    def __init__(self, questions: list[QuizQuestion]) -> None:
        self.questions = questions

    @classmethod
    def default_bank(cls) -> "QuestionBank":
        questions = [
            QuizQuestion(
                id=1,
                question="Python에서 리스트 길이를 구하는 함수는?",
                choices=["size()", "count()", "len()", "length()"],
                answer=3,
                hint="내장 함수다.",
            ),
            QuizQuestion(
                id=2,
                question="문자열을 정수로 변환하는 함수는?",
                choices=["str()", "int()", "float()", "bool()"],
                answer=2,
                hint="정수형 이름과 같다.",
            ),
            QuizQuestion(
                id=3,
                question="반복문에서 현재 반복만 건너뛰는 키워드는?",
                choices=["break", "skip", "continue", "pass"],
                answer=3,
                hint="다음 반복으로 넘어간다.",
            ),
            QuizQuestion(
                id=4,
                question="딕셔너리에서 키 목록과 관련 깊은 메서드는?",
                choices=["keys()", "values()", "items()", "get()"],
                answer=1,
                hint="키를 직접 보여준다.",
            ),
            QuizQuestion(
                id=5,
                question="함수를 정의할 때 사용하는 키워드는?",
                choices=["func", "define", "def", "lambda"],
                answer=3,
                hint="세 글자다.",
            ),
        ]
        return cls(questions)

    def get_all(self) -> list[QuizQuestion]:
        return self.questions

    def get_by_id(self, question_id: int) -> QuizQuestion | None:
        for question in self.questions:
            if question.id == question_id:
                return question
        return None

    def add_question(self, question: QuizQuestion) -> None:
        self.questions.append(question)

    def delete_question(self, question_id: int) -> bool:
        for index, question in enumerate(self.questions):
            if question.id == question_id:
                del self.questions[index]
                return True
        return False

    def next_id(self) -> int:
        if not self.questions:
            return 1
        return max(question.id for question in self.questions) + 1

    def build_quiz_set(self, random_enabled: bool, question_count: int | None) -> list[int]:
        ids = [question.id for question in self.questions]
        return ids if question_count is None else ids[:question_count]

    def to_dict_list(self) -> list[dict]:
        return [question.to_dict() for question in self.questions]


class StateStore:
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                raw = json.load(file)

            questions_raw = raw.get("questions", [])
            question_bank = QuestionBank(
                [QuizQuestion.from_dict(item) for item in questions_raw if isinstance(item, dict)]
            )

            if not question_bank.get_all():
                question_bank = QuestionBank.default_bank()

            game_state = GameState.from_dict(raw.get("current_session", {}))
            history = raw.get("history", [])
            settings = raw.get(
                "settings",
                {
                    "random_enabled": False,
                    "question_count": None,
                    "hint_enabled": False,
                },
            )

            return {
                "question_bank": question_bank,
                "game_state": game_state,
                "history": history,
                "settings": settings,
            }

        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return self.build_default_state()

    def save(
        self,
        question_bank: QuestionBank,
        game_state: GameState,
        history: list[dict],
        settings: dict,
    ) -> None:
        data = {
            "version": 1,
            "questions": question_bank.to_dict_list(),
            "settings": settings,
            "current_session": game_state.to_dict(),
            "history": history,
        }

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def build_default_state(self) -> dict:
        return {
            "question_bank": QuestionBank.default_bank(),
            "game_state": GameState(),
            "history": [],
            "settings": {
                "random_enabled": False,
                "question_count": None,
                "hint_enabled": False,
            },
        }
