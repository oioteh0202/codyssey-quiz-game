from __future__ import annotations


class CLIView:
    def show_main_menu(self, has_saved_session: bool) -> None:
        print("\n=== Quiz Game ===")
        print("1. 이어하기" if has_saved_session else "1. 퀴즈 시작")
        print("2. 문제 추가")
        print("3. 문제 목록 보기")
        print("4. 추가 기능")
        print("0. 종료")

    def show_bonus_menu(self) -> None:
        print("\n=== 추가 기능 ===")
        print("1. 랜덤 출제 설정")
        print("2. 문제 수 선택")
        print("3. 힌트 설정")
        print("4. 문제 삭제")
        print("5. 점수 히스토리 보기")
        print("0. 뒤로가기")

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")

    def prompt(self, message: str) -> str:
        return input(message)

    def prompt_menu_choice(self, message: str, valid_range: range) -> int:
        pass

    def display_question(
        self,
        question_text: str,
        choices: list[str],
        question_no: int,
        total_count: int,
    ) -> None:
        print(f"\n[{question_no}/{total_count}] {question_text}")
        for index, choice in enumerate(choices, start=1):
            print(f"{index}. {choice}")

    def prompt_answer(self) -> int:
        pass

    def prompt_new_question_data(self) -> dict:
        pass

    def display_question_list(self, questions: list[dict]) -> None:
        print("\n=== 문제 목록 ===")
        for question in questions:
            print(f'{question["id"]}. {question["question"]}')

    def display_result(self, correct_count: int, total_count: int) -> None:
        print("\n=== 결과 ===")
        print(f"점수: {correct_count}/{total_count}")

    def display_history(self, history: list[dict]) -> None:
        print("\n=== 점수 히스토리 ===")
        if not history:
            print("기록이 없습니다.")
            return

        for index, item in enumerate(history, start=1):
            print(
                f'{index}. {item.get("played_at", "unknown")} | '
                f'{item.get("correct_count", 0)}/{item.get("question_count", 0)}'
            )
