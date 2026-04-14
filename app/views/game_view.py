from __future__ import annotations

from app.utils.validators import parse_int_in_range


class GameView:
    def show_question(self, question_text: str, index: int, total: int) -> None:
        print(f"\n[{index}/{total}] {question_text}")

    def show_choices(self, choices: list[str]) -> None:
        for choice_index, choice_text in enumerate(choices, start=1):
            print(f"{choice_index}. {choice_text}")

    def prompt_choice(self, choice_count: int) -> int:
        raw_value = input("선택지를 입력하세요: ")
        return parse_int_in_range(raw_value, 1, choice_count, "선택지 번호")

    def show_answer_result(self, is_correct: bool) -> None:
        if is_correct:
            print("정답입니다.")
        else:
            print("오답입니다.")

    def show_final_score(self, score: int, total: int) -> None:
        print(f"최종 점수: {score}/{total}")

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"오류: {message}")
