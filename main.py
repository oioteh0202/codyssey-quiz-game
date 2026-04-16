from __future__ import annotations

from model import GameState, QuestionBank, StateStore
from view import CLIView


class QuizController:
    def __init__(self, view: CLIView, store: StateStore) -> None:
        self.view = view
        self.store = store
        self.question_bank: QuestionBank | None = None
        self.game_state: GameState | None = None
        self.history: list[dict] = []
        self.settings: dict = {}

    def bootstrap(self) -> None:
        """프로그램 시작 시 state.json 자동 로드"""
        data = self.store.load()
        self.question_bank = data["question_bank"]
        self.game_state = data["game_state"]
        self.history = data["history"]
        self.settings = data["settings"]

    def run(self) -> None:
        """메인 메뉴 루프"""
        while True:
            has_saved_session = bool(self.game_state and self.game_state.in_progress)
            self.view.show_main_menu(has_saved_session)
            choice = self.view.prompt_menu_choice("메뉴 선택: ", range(0, 5))

            should_continue = self.handle_main_menu(choice)
            if not should_continue:
                break

    def handle_main_menu(self, choice: int) -> bool:
        """메인 메뉴 선택 처리. 종료 시 False 반환"""
        # 지금 단계에서는 실제 기능 대신 메뉴 흐름만 연결한다.
        if choice == 1:
            self.view.show_message("퀴즈 시작/이어하기는 다음 단계에서 구현합니다.")
            return True

        if choice == 2:
            self.view.show_message("문제 추가는 다음 단계에서 구현합니다.")
            return True

        if choice == 3:
            self.show_question_list()
            return True

        if choice == 4:
            self.view.show_message("추가 기능은 다음 단계에서 구현합니다.")
            return True

        if choice == 0:
            self.save_state()
            self.view.show_message("프로그램을 종료합니다.")
            return False

        self.view.show_error("잘못된 메뉴 선택입니다.")
        return True

    def start_or_resume_quiz(self) -> None:
        """새 게임 시작 또는 이어하기"""
        pass

    def play_quiz(self) -> None:
        """실제 퀴즈 진행"""
        pass

    def add_question(self) -> None:
        """문제 추가"""
        pass

    def show_question_list(self) -> None:
        """문제 목록 보기"""
        if self.question_bank is None:
            self.view.show_error("문제 목록을 불러오지 못했습니다.")
            return

        questions = self.question_bank.get_all()
        if not questions:
            self.view.show_message("등록된 문제가 없습니다.")
            return

        question_dicts = []
        for question in questions:
            question_dicts.append(
                {
                    "id": question.id,
                    "question": question.question,
                }
            )

        self.view.display_question_list(question_dicts)

    def open_bonus_menu(self) -> None:
        """보너스 기능 메뉴"""
        pass

    def save_state(self) -> None:
        """현재 상태 저장"""
        if self.question_bank is None or self.game_state is None:
            return

        self.store.save(
            question_bank=self.question_bank,
            game_state=self.game_state,
            history=self.history,
            settings=self.settings,
        )

    def finalize_completed_session(self) -> None:
        """게임 완료 시 history 반영 후 current_session 정리"""
        pass


def main() -> None:
    view = CLIView()
    store = StateStore("state.json")
    controller = QuizController(view, store)
    controller.bootstrap()
    controller.run()


if __name__ == "__main__":
    main()
