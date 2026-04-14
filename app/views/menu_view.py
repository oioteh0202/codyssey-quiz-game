from __future__ import annotations

from app.utils.validators import parse_int_in_range


class MenuView:
    def show_main_menu(self) -> None:
        print("\n=== 퀴즈 게임 ===")
        print("1. 새 게임")
        print("2. 불러오기")
        print("3. 종료")
        print("4. 퀴즈 삭제")

    def prompt_main_menu_choice(self) -> int:
        raw_value = input("메뉴를 선택하세요: ")
        return parse_int_in_range(raw_value, 1, 4, "메뉴 번호")

    def show_quiz_list(self, quiz_items: list[tuple[int, str]]) -> None:
        print("\n=== 등록된 퀴즈 ===")
        for index, text in quiz_items:
            print(f"{index}. {text}")

    def prompt_delete_quiz_index(self, total_count: int) -> int:
        raw_value = input("삭제할 퀴즈 번호를 입력하세요: ")
        return parse_int_in_range(raw_value, 1, total_count, "퀴즈 번호")

    def prompt_save_on_exit(self) -> bool:
        raw_value = input("진행 상황을 저장할까요? (y/n): ").strip().lower()
        return raw_value in {"y", "yes"}

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"오류: {message}")
