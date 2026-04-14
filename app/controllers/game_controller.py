from __future__ import annotations

from collections.abc import Callable

from app.models.quiz_session import QuizSession
from app.views.game_view import GameView


class GameController:
    def __init__(
        self,
        session: QuizSession,
        game_view: GameView | None = None,
        on_progress: Callable[[QuizSession], None] | None = None,
    ) -> None:
        self._session = session
        self._view = game_view or GameView()
        self._on_progress = on_progress

    @property
    def session(self) -> QuizSession:
        return self._session

    def run(self) -> bool:
        interrupted = False

        while not self._session.is_finished():
            question = self._session.current_question()
            if question is None:
                break

            self._view.show_question(
                question_text=question.text,
                index=self._session.current_index + 1,
                total=self._session.total_questions,
            )
            self._view.show_choices(question.choices)

            selected_index = self._prompt_choice(len(question.choices))
            if selected_index is None:
                interrupted = True
                break

            selected_answer = question.choices[selected_index - 1]
            is_correct = self._session.submit_answer(selected_answer)
            self._view.show_answer_result(is_correct)
            self._session.next_question()
            self._save_progress()

        if not interrupted:
            self._view.show_final_score(self._session.score, self._session.total_questions)
            self._save_progress()

        return not interrupted

    def _prompt_choice(self, choice_count: int) -> int | None:
        while True:
            try:
                return self._view.prompt_choice(choice_count)
            except ValueError as error:
                self._view.show_error(str(error))
            except (KeyboardInterrupt, EOFError):
                self._view.show_message("입력이 중단되었습니다.")
                return None

    def _save_progress(self) -> None:
        if self._on_progress is not None:
            self._on_progress(self._session)
