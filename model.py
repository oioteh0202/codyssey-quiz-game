from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json
import random

@dataclass
class QuizQuestion:
    # 퀴즈 문제 1개를 표현하는 데이터 클래스
    id: int
    question: str
    choices: list[str]
    answer: int
    hint: Optional[str] = None

    def is_valid(self) -> bool:
        # 문제 데이터가 과제 조건에 맞는지 검사한다.
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
        # JSON 저장을 위해 객체를 dict 형태로 바꾼다.
        return {
            "id": self.id,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QuizQuestion":
        # JSON에서 읽은 dict를 QuizQuestion 객체로 복원한다.
        return cls(
            id=data["id"],
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint"),
        )


@dataclass
class GameState:
    # 현재 진행 중인 게임 상태를 저장하는 데이터 클래스
    in_progress: bool = False
    question_ids: list[int] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0
    answers: list[dict] = field(default_factory=list)
    options: dict = field(default_factory=dict)

    def start_new(self, question_ids: list[int], options: dict) -> None:
        # 새 게임을 시작할 때 상태를 초기화한다.
        self.in_progress = True
        self.question_ids = question_ids
        self.current_index = 0
        self.correct_count = 0
        self.answers = []
        self.options = options

    def record_answer(self, question_id: int, selected: int, correct: bool) -> None:
        # 사용자의 답변 결과를 기록한다.
        self.answers.append(
            {
                "question_id": question_id,
                "selected": selected,
                "correct": correct,
            }
        )

        # 정답이면 맞춘 개수를 증가시킨다.
        if correct:
            self.correct_count += 1

        # 다음 문제로 넘어가기 위해 현재 인덱스를 증가시킨다.
        self.current_index += 1

    def is_finished(self) -> bool:
        # 현재 인덱스가 전체 문제 수에 도달했는지 검사한다.
        return self.in_progress and self.current_index >= len(self.question_ids)

    def clear(self) -> None:
        # 게임이 끝났거나 취소되었을 때 상태를 비운다.
        self.in_progress = False
        self.question_ids = []
        self.current_index = 0
        self.correct_count = 0
        self.answers = []
        self.options = {}

    def to_dict(self) -> dict:
        # JSON 저장을 위해 현재 상태를 dict로 변환한다.
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
        # JSON에서 읽은 dict를 GameState 객체로 복원한다.
        return cls(
            in_progress=data.get("in_progress", False),
            question_ids=data.get("question_ids", []),
            current_index=data.get("current_index", 0),
            correct_count=data.get("correct_count", 0),
            answers=data.get("answers", []),
            options=data.get("options", {}),
        )


class QuestionBank:
    # 전체 문제 목록을 관리하는 클래스
    def __init__(self, questions: list[QuizQuestion]) -> None:
        self.questions = questions

    @classmethod
    def default_bank(cls) -> "QuestionBank":
        # state.json이 없거나 손상됐을 때 사용할 기본 문제 세트다.
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
        # 등록된 전체 문제 목록을 반환한다.
        return self.questions

    def get_by_id(self, question_id: int) -> QuizQuestion | None:
        # 문제 id로 특정 문제를 찾는다.
        for question in self.questions:
            if question.id == question_id:
                return question
        return None

    def add_question(self, question: QuizQuestion) -> None:
        # 새 문제를 문제 목록에 추가한다.
        self.questions.append(question)

    def delete_question(self, question_id: int) -> bool:
        # 문제 id와 일치하는 문제를 삭제한다.
        for index, question in enumerate(self.questions):
            if question.id == question_id:
                del self.questions[index]
                return True
        return False

    def next_id(self) -> int:
        # 새 문제를 추가할 때 사용할 다음 id를 계산한다.
        if not self.questions:
            return 1
        return max(question.id for question in self.questions) + 1

    def build_quiz_set(self, random_enabled: bool, question_count: int | None) -> list[int]:
        # 현재 등록된 문제 id 목록을 만든다.
        ids = [question.id for question in self.questions]

        # 랜덤 출제가 켜져 있으면 문제 순서를 섞는다.
        if random_enabled:
            random.shuffle(ids)

        # question_count가 None이면 전체 문제를 그대로 사용한다.
        if question_count is None:
            return ids

        # 문제 수가 설정되어 있으면 앞에서부터 필요한 개수만 사용한다.
        return ids[:question_count]

    def to_dict_list(self) -> list[dict]:
        # 전체 문제 목록을 JSON 저장 가능한 dict 리스트로 변환한다.
        return [question.to_dict() for question in self.questions]


class StateStore:
    # state.json 파일 입출력을 담당하는 저장소 클래스
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> dict:
        try:
            # 저장 파일을 읽어 JSON 데이터를 불러온다.
            with open(self.path, "r", encoding="utf-8") as file:
                raw = json.load(file)

            # 최상위 구조가 dict가 아니면 손상된 파일로 보고 기본 상태를 사용한다.
            if not isinstance(raw, dict):
                return self.build_default_state()

            # questions는 리스트여야 한다. 아니면 빈 리스트로 처리한다.
            questions_raw = raw.get("questions", [])
            if not isinstance(questions_raw, list):
                questions_raw = []

            valid_questions = []

            # 문제 하나가 손상돼도 전체 로드를 망치지 않도록 개별 복원한다.
            for item in questions_raw:
                if not isinstance(item, dict):
                    continue

                try:
                    question = QuizQuestion.from_dict(item)
                except (KeyError, TypeError, ValueError):
                    continue

                if question.is_valid():
                    valid_questions.append(question)

            question_bank = QuestionBank(valid_questions)

            # 유효한 문제가 하나도 없으면 기본 문제 세트로 대체한다.
            if not question_bank.get_all():
                question_bank = QuestionBank.default_bank()

            # current_session은 dict여야 한다. 아니면 빈 상태로 처리한다.
            current_session_raw = raw.get("current_session", {})
            if not isinstance(current_session_raw, dict):
                current_session_raw = {}
            game_state = GameState.from_dict(current_session_raw)

            # history는 리스트여야 한다. 아니면 빈 리스트로 처리한다.
            history = raw.get("history", [])
            if not isinstance(history, list):
                history = []

            # settings는 dict여야 한다. 아니면 기본 설정으로 처리한다.
            settings = raw.get("settings", {})
            if not isinstance(settings, dict):
                settings = {}

            settings = {
                "random_enabled": bool(settings.get("random_enabled", False)),
                "question_count": settings.get("question_count"),
                "hint_enabled": bool(settings.get("hint_enabled", False)),
            }

            return {
                "question_bank": question_bank,
                "game_state": game_state,
                "history": history,
                "settings": settings,
            }

        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError, KeyError, OSError):
            # 파일이 없거나 손상된 경우에도 프로그램이 실행되도록 기본 상태를 반환한다.
            return self.build_default_state()

    def save(
        self,
        question_bank: QuestionBank,
        game_state: GameState,
        history: list[dict],
        settings: dict,
    ) -> None:
        # 현재 상태를 JSON 구조에 맞춰 정리한다.
        data = {
            "version": 1,
            "questions": question_bank.to_dict_list(),
            "settings": settings,
            "current_session": game_state.to_dict(),
            "history": history,
        }

        # 한글이 깨지지 않도록 UTF-8로 저장한다.
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def build_default_state(self) -> dict:
        # 기본 실행 상태를 구성한다.
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