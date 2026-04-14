from __future__ import annotations

import json
from pathlib import Path

from app.controllers.game_controller import GameController
from app.models.question_bank import QuestionBank
from app.models.quiz_session import QuizSession
from app.models.state_repository import StateRepository
from app.views.menu_view import MenuView


class AppController:
    def __init__(
        self,
        menu_view: MenuView | None = None,
        questions_path: str | Path = "data/questions.json",
        state_path: str | Path = "state.json",
    ) -> None:
        self._menu_view = menu_view or MenuView()
        self._questions_path = Path(questions_path)
        self._state_repository = StateRepository(state_path)

    def run(self) -> None:
        while True:
            self._menu_view.show_main_menu()
            try:
                choice = self._menu_view.prompt_main_menu_choice()
            except ValueError as error:
                self._menu_view.show_error(str(error))
                continue
            except (KeyboardInterrupt, EOFError):
                self._menu_view.show_message("입력이 종료되어 프로그램을 종료합니다.")
                break

            if choice == 1:
                self._start_new_game()
            elif choice == 2:
                self._load_game()
            elif choice == 3:
                break
            elif choice == 4:
                self._delete_quiz()

    def _start_new_game(self) -> None:
        try:
            question_bank = QuestionBank.from_json(self._questions_path)
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            self._menu_view.show_error("문제를 불러올 수 없습니다.")
            return

        session = QuizSession(question_bank.shuffled().questions)
        game_controller = GameController(session=session, on_progress=self._save_session)
        completed = game_controller.run()

        if not completed:
            self._ask_save_on_interrupt(session)

    def _load_game(self) -> None:
        try:
            state = self._state_repository.load()
        except FileNotFoundError:
            self._menu_view.show_error("저장된 게임이 없습니다.")
            return
        except ValueError:
            self._menu_view.show_error("저장 파일이 손상되었거나 읽을 수 없습니다.")
            return

        try:
            question_bank = QuestionBank.from_json(self._questions_path)
            session = QuizSession.from_dict(state, question_bank.questions)
        except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError, TypeError):
            self._menu_view.show_error("저장 게임을 불러올 수 없습니다.")
            return

        game_controller = GameController(session=session, on_progress=self._save_session)
        completed = game_controller.run()

        if not completed:
            self._ask_save_on_interrupt(session)

    def _delete_quiz(self) -> None:
        try:
            question_bank = QuestionBank.from_json(self._questions_path)
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            self._menu_view.show_error("문제를 불러올 수 없습니다.")
            return

        questions = question_bank.questions
        if not questions:
            self._menu_view.show_error("삭제할 퀴즈가 없습니다.")
            return

        self._menu_view.show_quiz_list([(i + 1, q.text) for i, q in enumerate(questions)])

        try:
            delete_index = self._menu_view.prompt_delete_quiz_index(len(questions))
        except ValueError as error:
            self._menu_view.show_error(str(error))
            return
        except (KeyboardInterrupt, EOFError):
            self._menu_view.show_message("삭제 입력이 취소되었습니다.")
            return

        try:
            deleted = question_bank.delete_by_index(delete_index)
            question_bank.save_json(self._questions_path)
        except (ValueError, OSError):
            self._menu_view.show_error("퀴즈 삭제를 저장하지 못했습니다.")
            return

        self._menu_view.show_message(f"퀴즈가 삭제되었습니다: {deleted.text}")

    def _ask_save_on_interrupt(self, session: QuizSession) -> None:
        try:
            should_save = self._menu_view.prompt_save_on_exit()
        except (KeyboardInterrupt, EOFError):
            self._menu_view.show_message("저장 선택이 취소되어 저장하지 않고 종료합니다.")
            return

        if should_save:
            self._save_session(session)
            self._menu_view.show_message("진행 상황이 저장되었습니다.")
        else:
            self._menu_view.show_message("저장하지 않고 종료합니다.")

    def _save_session(self, session: QuizSession) -> None:
        try:
            self._state_repository.save(session.to_dict())
        except OSError:
            self._menu_view.show_error("저장 중 오류가 발생했습니다.")
