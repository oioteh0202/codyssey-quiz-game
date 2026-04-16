from __future__ import annotations
from datetime import datetime
from model import GameState, QuestionBank, StateStore
from view import CLIView
from model import GameState, QuestionBank, QuizQuestion, StateStore

class QuizController:
    def __init__(self, view: CLIView, store: StateStore) -> None:
        # View: 화면 출력과 입력 담당
        self.view = view

        # Store: state.json 저장/불러오기 담당
        self.store = store

        # 프로그램 시작 후 bootstrap()에서 실제 데이터가 주입된다.
        self.question_bank: QuestionBank | None = None
        self.game_state: GameState | None = None
        self.history: list[dict] = []
        self.settings: dict = {}

    def bootstrap(self) -> None:
        """프로그램 시작 시 state.json 자동 로드"""
        # 저장소에서 현재 상태를 읽어와 Controller 내부 상태에 반영한다.
        data = self.store.load()
        self.question_bank = data["question_bank"]
        self.game_state = data["game_state"]
        self.history = data["history"]
        self.settings = data["settings"]

    def run(self) -> None:
        """메인 메뉴 루프"""
        # 사용자가 종료를 선택할 때까지 메인 메뉴를 반복한다.
        while True:
            try:
                # 진행 중 세션이 있으면 메뉴 1번을 '이어하기'로 보여주기 위해 상태를 계산한다.
                has_saved_session = bool(self.game_state and self.game_state.in_progress)

                # 현재 상태에 맞는 메인 메뉴를 출력한다.
                self.view.show_main_menu(has_saved_session)

                # 메뉴 번호 입력을 받고, 0~4 범위만 허용한다.
                choice = self.view.prompt_menu_choice("메뉴 선택: ", range(0, 5))

                # 선택한 메뉴를 처리한다.
                should_continue = self.handle_main_menu(choice)

                # False가 반환되면 프로그램을 종료한다.
                if not should_continue:
                    break

            except (KeyboardInterrupt, EOFError):
                # 메인 메뉴에서 중단되면 현재 상태를 저장하고 종료한다.
                self.save_state()
                self.view.show_message("\n프로그램을 종료합니다.")
                break

    def handle_main_menu(self, choice: int) -> bool:
        """메인 메뉴 선택 처리. 종료 시 False 반환"""
        if choice == 1:
            self.start_or_resume_quiz()
            return True

        if choice == 2:
            self.add_question()
            return True

        if choice == 3:
            # 현재 등록된 문제 목록을 출력한다.
            self.show_question_list()
            return True

        if choice == 4:
            self.open_bonus_menu()
            return True

        if choice == 0:
            # 종료 전에 현재 상태를 저장한다.
            self.save_state()
            self.view.show_message("프로그램을 종료합니다.")
            return False

        # 이 분기는 입력 검증이 제대로 되면 사실상 도달하지 않는다.
        self.view.show_error("잘못된 메뉴 선택입니다.")
        return True

    def start_or_resume_quiz(self) -> None:
        """새 게임 시작 또는 이어하기"""
        if self.question_bank is None or self.game_state is None:
            self.view.show_error("게임을 시작할 수 없습니다.")
            return

        # 진행 중인 게임이 없으면 새 세션을 만든다.
        if not self.game_state.in_progress:
            question_ids = self.question_bank.build_quiz_set(
                random_enabled=self.settings.get("random_enabled", False),
                question_count=self.settings.get("question_count"),
            )

            if not question_ids:
                self.view.show_message("출제할 문제가 없습니다.")
                return

            options = {
                "random_enabled": self.settings.get("random_enabled", False),
                "question_count": self.settings.get("question_count"),
                "hint_enabled": self.settings.get("hint_enabled", False),
            }

            self.game_state.start_new(question_ids, options)

        self.play_quiz()

    def play_quiz(self) -> None:
        """실제 퀴즈 진행"""
        if self.question_bank is None or self.game_state is None:
            self.view.show_error("게임 상태를 불러오지 못했습니다.")
            return

        total_count = len(self.game_state.question_ids)

        while not self.game_state.is_finished():
            question_id = self.game_state.question_ids[self.game_state.current_index]
            question = self.question_bank.get_by_id(question_id)

            if question is None:
                self.view.show_error("문제를 불러오지 못했습니다.")
                return

            # 현재 문제와 보기 4개를 출력한다.
            self.view.display_question(
                question_text=question.question,
                choices=question.choices,
                question_no=self.game_state.current_index + 1,
                total_count=total_count,
            )

            try:
                selected = self.view.prompt_answer()
            except (KeyboardInterrupt, EOFError):
                # 퀴즈 진행 중 중단되면 현재 세션을 저장하고 메인 메뉴로 돌아간다.
                self.save_state()
                self.view.show_message("\n퀴즈를 중단하고 메인 메뉴로 돌아갑니다.")
                return

            is_correct = selected == question.answer

            self.game_state.record_answer(
                question_id=question.id,
                selected=selected,
                correct=is_correct,
            )

            # 답을 입력한 직후 정오답 안내를 보여준다.
            if is_correct:
                self.view.show_message("정답입니다.")
            else:
                self.view.show_message(f"오답입니다. 정답은 {question.answer}번입니다.")

        self.view.display_result(self.game_state.correct_count, total_count)
        self.finalize_completed_session()
        self.save_state()

    def add_question(self) -> None:
        """문제 추가"""
        if self.question_bank is None:
            self.view.show_error("문제 은행을 불러오지 못했습니다.")
            return

        try:
            # View에서 문제 문장, 보기 4개, 정답 번호, 힌트를 입력받는다.
            question_data = self.view.prompt_new_question_data()
        except (KeyboardInterrupt, EOFError):
            # 입력 도중 중단되면 현재 작업만 취소하고 메인 메뉴로 돌아간다.
            self.view.show_message("\n문제 추가를 취소하고 메인 메뉴로 돌아갑니다.")
            return

        # 새 문제는 QuestionBank에서 다음 id를 받아 생성한다.
        new_question = QuizQuestion(
            id=self.question_bank.next_id(),
            question=question_data["question"],
            choices=question_data["choices"],
            answer=question_data["answer"],
            hint=question_data["hint"],
        )

        # 문제 데이터가 과제 조건에 맞지 않으면 추가하지 않는다.
        if not new_question.is_valid():
            self.view.show_error("문제 형식이 올바르지 않아 추가하지 못했습니다.")
            return

        self.question_bank.add_question(new_question)
        self.save_state()
        self.view.show_message("새 문제가 추가되었습니다.")

    def show_question_list(self) -> None:
        """문제 목록 보기"""
        # 문제 은행이 비어 있거나 초기화되지 않은 경우를 먼저 막는다.
        if self.question_bank is None:
            self.view.show_error("문제 목록을 불러오지 못했습니다.")
            return

        # QuestionBank에서 전체 문제 목록을 가져온다.
        questions = self.question_bank.get_all()

        # 문제가 하나도 없으면 안내 메시지를 출력한다.
        if not questions:
            self.view.show_message("등록된 문제가 없습니다.")
            return

        # View에는 필요한 데이터만 넘기기 위해 단순 dict 형태로 변환한다.
        question_dicts = []
        for question in questions:
            question_dicts.append(
                {
                    "id": question.id,
                    "question": question.question,
                }
            )

        # 변환된 문제 목록을 화면에 출력한다.
        self.view.display_question_list(question_dicts)

    def open_bonus_menu(self) -> None:
        """보너스 기능 메뉴"""
        # 보너스 기능은 별도 하위 메뉴에서 처리한다.
        while True:
            self.view.show_bonus_menu()
            choice = self.view.prompt_menu_choice("추가 기능 선택: ", range(0, 6))

            if choice == 1:
                self.toggle_random_mode()
                continue

            if choice == 2:
                self.select_question_count()
                continue

            if choice == 3:
                self.view.show_message("힌트 설정은 다음 단계에서 구현합니다.")
                continue

            if choice == 4:
                self.delete_question()
                continue

            if choice == 5:
                # 저장된 점수 기록을 그대로 출력한다.
                self.view.display_history(self.history)
                continue

            if choice == 0:
                # 0번을 누르면 메인 메뉴로 돌아간다.
                self.view.show_message("메인 메뉴로 돌아갑니다.")
                return

    def toggle_random_mode(self) -> None:
        """랜덤 출제 설정"""
        current = self.settings.get("random_enabled", False)

        # 진행 중인 게임이 있으면 현재 세션에는 영향을 주지 않는다고 안내한다.
        if self.game_state is not None and self.game_state.in_progress:
            self.view.show_message("현재 진행 중인 게임에는 적용되지 않고, 다음 새 게임부터 적용됩니다.")

        # 현재 상태를 반전시켜 ON/OFF 토글로 처리한다.
        new_value = not current
        self.settings["random_enabled"] = new_value
        self.save_state()

        status = "ON" if new_value else "OFF"
        self.view.show_message(f"랜덤 출제 설정이 {status}로 저장되었습니다.")

    def select_question_count(self) -> None:
        """문제 수 선택"""
        if self.question_bank is None:
            self.view.show_error("문제 목록을 불러오지 못했습니다.")
            return

        total_questions = len(self.question_bank.get_all())
        if total_questions == 0:
            self.view.show_message("설정할 문제가 없습니다.")
            return

        # 진행 중 게임이 있으면 현재 세션에는 영향을 주지 않는다고 안내한다.
        if self.game_state is not None and self.game_state.in_progress:
            self.view.show_message("현재 진행 중인 게임에는 적용되지 않고, 다음 새 게임부터 적용됩니다.")

        self.view.show_message(f"현재 등록된 문제 수: {total_questions}")
        self.view.show_message("출제할 문제 수를 입력하세요. (전체 출제: 0)")

        while True:
            try:
                raw = self.view.prompt("문제 수 선택: ").strip()
            except (KeyboardInterrupt, EOFError):
                self.view.show_message("\n문제 수 선택을 취소하고 보너스 메뉴로 돌아갑니다.")
                return

            if raw == "":
                self.view.show_error("빈 입력은 허용되지 않습니다.")
                continue

            try:
                count = int(raw)
            except ValueError:
                self.view.show_error("숫자만 입력해 주세요.")
                continue

            if count < 0 or count > total_questions:
                self.view.show_error(f"0부터 {total_questions} 사이의 숫자를 입력해 주세요.")
                continue

            # 0은 전체 문제 출제를 뜻하므로 None으로 저장한다.
            if count == 0:
                self.settings["question_count"] = None
                self.save_state()
                self.view.show_message("문제 수 설정이 '전체 출제'로 저장되었습니다.")
                return

            self.settings["question_count"] = count
            self.save_state()
            self.view.show_message(f"문제 수가 {count}개로 저장되었습니다.")
            return

    def delete_question(self) -> None:
        """문제 삭제"""
        if self.question_bank is None:
            self.view.show_error("문제 목록을 불러오지 못했습니다.")
            return

        # 진행 중인 게임이 있으면 출제 목록과 충돌할 수 있으므로 삭제를 막는다.
        if self.game_state is not None and self.game_state.in_progress:
            self.view.show_error("진행 중인 게임이 있을 때는 문제를 삭제할 수 없습니다.")
            return

        questions = self.question_bank.get_all()
        if not questions:
            self.view.show_message("삭제할 문제가 없습니다.")
            return

        # 먼저 현재 문제 목록을 보여주고, 사용자가 id를 보고 선택하게 한다.
        self.show_question_list()

        while True:
            try:
                raw = self.view.prompt("삭제할 문제 id를 입력하세요 (취소: 0): ").strip()
            except (KeyboardInterrupt, EOFError):
                self.view.show_message("\n문제 삭제를 취소하고 보너스 메뉴로 돌아갑니다.")
                return

            if raw == "":
                self.view.show_error("빈 입력은 허용되지 않습니다.")
                continue

            try:
                question_id = int(raw)
            except ValueError:
                self.view.show_error("숫자만 입력해 주세요.")
                continue

            if question_id == 0:
                self.view.show_message("문제 삭제를 취소합니다.")
                return

            if question_id < 0:
                self.view.show_error("0 이상의 번호를 입력해 주세요.")
                continue

            target = self.question_bank.get_by_id(question_id)
            if target is None:
                self.view.show_error("해당 id의 문제가 없습니다.")
                continue

            deleted = self.question_bank.delete_question(question_id)
            if not deleted:
                self.view.show_error("문제를 삭제하지 못했습니다.")
                return

            self.save_state()
            self.view.show_message(f"{question_id}번 문제가 삭제되었습니다.")
            return

    def save_state(self) -> None:
        """현재 상태 저장"""
        # 저장에 필요한 핵심 객체가 없으면 저장하지 않는다.
        if self.question_bank is None or self.game_state is None:
            return

        # 현재 문제 목록, 진행 상태, 히스토리, 설정을 파일에 저장한다.
        self.store.save(
            question_bank=self.question_bank,
            game_state=self.game_state,
            history=self.history,
            settings=self.settings,
        )

    def finalize_completed_session(self) -> None:
        """게임 완료 시 history 반영 후 current_session 정리"""
        if self.game_state is None:
            return

        if not self.game_state.is_finished():
            return

        total_count = len(self.game_state.question_ids)
        wrong_count = total_count - self.game_state.correct_count

        # 완료된 게임 결과를 히스토리에 남긴다.
        self.history.append(
            {
                "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "question_count": total_count,
                "correct_count": self.game_state.correct_count,
                "wrong_count": wrong_count,
                "random_enabled": self.game_state.options.get("random_enabled", False),
                "hint_used_count": 0,
            }
        )

        # 완료된 세션은 이어하기 대상이 아니므로 초기화한다.
        self.game_state.clear()


def main() -> None:
    # 프로그램에서 사용할 View와 Store를 생성한다.
    view = CLIView()
    store = StateStore("state.json")

    # Controller를 만들고, 저장된 상태를 불러온 뒤 실행한다.
    controller = QuizController(view, store)
    controller.bootstrap()
    controller.run()


if __name__ == "__main__":
    main()