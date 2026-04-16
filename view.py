from __future__ import annotations


class CLIView:
    def show_main_menu(self, has_saved_session: bool) -> None:
        # 진행 중 세션이 있으면 1번 메뉴를 '이어하기'로 보여준다.
        print("\n=== Quiz Game ===")
        print("1. 이어하기" if has_saved_session else "1. 퀴즈 시작")
        print("2. 문제 추가")
        print("3. 문제 목록 보기")
        print("4. 추가 기능")
        print("0. 종료")

    def show_bonus_menu(self) -> None:
        # 보너스 기능은 핵심 기능과 분리된 하위 메뉴로 보여준다.
        print("\n=== 추가 기능 ===")
        print("1. 랜덤 출제 설정")
        print("2. 문제 수 선택")
        print("3. 힌트 설정")
        print("4. 문제 삭제")
        print("5. 점수 히스토리 보기")
        print("0. 뒤로가기")

    def show_message(self, message: str) -> None:
        # 일반 안내 메시지를 출력한다.
        print(message)

    def show_error(self, message: str) -> None:
        # 오류 메시지는 보기 쉽게 [오류] 접두어를 붙인다.
        print(f"[오류] {message}")

    def prompt(self, message: str) -> str:
        # 실제 입력은 View에서만 받도록 분리한다.
        return input(message)

    def prompt_menu_choice(self, message: str, valid_range: range) -> int:
        # 메뉴 입력은 공백/문자/범위 이탈을 모두 막는다.
        while True:
            # 앞뒤 공백을 제거해 ' 1 ' 같은 입력도 정상 처리한다.
            raw = self.prompt(message).strip()

            # 빈 문자열은 유효한 입력으로 보지 않는다.
            if raw == "":
                self.show_error("빈 입력은 허용되지 않습니다.")
                continue

            # 숫자로 변환되지 않으면 다시 입력받는다.
            try:
                choice = int(raw)
            except ValueError:
                self.show_error("숫자만 입력해 주세요.")
                continue

            # 허용 범위를 벗어나면 다시 입력받는다.
            if choice not in valid_range:
                min_value = valid_range.start
                max_value = valid_range.stop - 1
                self.show_error(f"{min_value}부터 {max_value} 사이의 번호를 입력해 주세요.")
                continue

            # 여기까지 왔으면 정상 입력이므로 정수값을 반환한다.
            return choice

    def display_question(
        self,
        question_text: str,
        choices: list[str],
        question_no: int,
        total_count: int,
    ) -> None:
        # 현재 몇 번째 문제인지 함께 출력해 진행 상황을 보여준다.
        print(f"\n[{question_no}/{total_count}] {question_text}")

        # 보기 번호는 과제 조건에 맞게 1~4 체계로 출력한다.
        for index, choice in enumerate(choices, start=1):
            print(f"{index}. {choice}")

    def prompt_answer(self) -> int:
        # 정답 입력은 1~4 번호 체계만 허용한다.
        while True:
            try:
                raw = self.prompt("정답을 입력하세요 (1~4): ").strip()
            except (KeyboardInterrupt, EOFError):
                # 종료/중단 흐름 결정은 Controller가 하도록 예외를 다시 넘긴다.
                raise

            # 빈 입력은 허용하지 않는다.
            if raw == "":
                self.show_error("빈 입력은 허용되지 않습니다.")
                continue

            # 숫자가 아니면 다시 입력받는다.
            try:
                answer = int(raw)
            except ValueError:
                self.show_error("1부터 4 사이의 숫자만 입력해 주세요.")
                continue

            # 1~4 범위를 벗어나면 다시 입력받는다.
            if answer < 1 or answer > 4:
                self.show_error("정답 번호는 1부터 4까지만 입력할 수 있습니다.")
                continue

            return answer

    def prompt_new_question_data(self) -> dict:
        # 문제 추가에 필요한 입력을 순서대로 받아 dict 형태로 반환한다.
        while True:
            try:
                question = self.prompt("문제를 입력하세요: ").strip()
            except (KeyboardInterrupt, EOFError):
                # 중단 처리 정책은 Controller가 결정하도록 예외를 다시 넘긴다.
                raise

            if question == "":
                self.show_error("문제 문장은 비워둘 수 없습니다.")
                continue
            break

        choices = []
        for index in range(1, 5):
            while True:
                try:
                    choice = self.prompt(f"{index}번 보기를 입력하세요: ").strip()
                except (KeyboardInterrupt, EOFError):
                    raise

                if choice == "":
                    self.show_error("보기는 비워둘 수 없습니다.")
                    continue

                choices.append(choice)
                break

        while True:
            try:
                raw_answer = self.prompt("정답 번호를 입력하세요 (1~4): ").strip()
            except (KeyboardInterrupt, EOFError):
                raise

            if raw_answer == "":
                self.show_error("정답 번호는 비워둘 수 없습니다.")
                continue

            try:
                answer = int(raw_answer)
            except ValueError:
                self.show_error("정답 번호는 1부터 4 사이의 숫자여야 합니다.")
                continue

            if answer < 1 or answer > 4:
                self.show_error("정답 번호는 1부터 4까지만 입력할 수 있습니다.")
                continue

            break

        try:
            hint_raw = self.prompt("힌트를 입력하세요 (없으면 엔터): ").strip()
        except (KeyboardInterrupt, EOFError):
            raise

        # 힌트는 선택 입력이므로 빈 문자열이면 None으로 통일한다.
        hint = hint_raw if hint_raw != "" else None

        return {
            "question": question,
            "choices": choices,
            "answer": answer,
            "hint": hint,
        }

    def display_question_list(self, questions: list[dict]) -> None:
        # 등록된 문제의 id와 문제 문장만 간단히 출력한다.
        print("\n=== 문제 목록 ===")
        for question in questions:
            print(f'{question["id"]}. {question["question"]}')

    def display_result(self, correct_count: int, total_count: int) -> None:
        # 게임 종료 후 최종 점수를 출력한다.
        print("\n=== 결과 ===")
        print(f"점수: {correct_count}/{total_count}")

    def display_history(self, history: list[dict]) -> None:
        # 저장된 점수 기록을 순서대로 보여준다.
        print("\n=== 점수 히스토리 ===")

        # 기록이 없으면 빈 목록 대신 안내 메시지를 출력한다.
        if not history:
            print("기록이 없습니다.")
            return

        # 날짜와 점수를 한 줄씩 출력한다.
        for index, item in enumerate(history, start=1):
            print(
                f'{index}. {item.get("played_at", "unknown")} | '
                f'{item.get("correct_count", 0)}/{item.get("question_count", 0)}'
            )