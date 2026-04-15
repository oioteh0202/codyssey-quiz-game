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
        pass

    def handle_main_menu(self, choice: int) -> bool:
        """메인 메뉴 선택 처리. 종료 시 False 반환"""
        pass

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
        pass

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
