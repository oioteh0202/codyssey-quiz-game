from quiz import Quiz
from storage import load_state, save_state


class QuizGame:
    def __init__(self):
        state = load_state()

        if state["quizzes"]:
            self.quizzes = [Quiz.from_dict(item) for item in state["quizzes"]]
        else:
            self.quizzes = [
                Quiz("Python의 창시자는 누구인가?", "귀도 반 로섬"),
                Quiz("2 + 2는 얼마인가?", "4"),
            ]

        self.high_score = state["high_score"]

    def show_menu(self):
        print("\n==== 퀴즈 게임 ====")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")

    def list_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print("\n[퀴즈 목록]")
        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"{index}. {quiz.question}")

    def save(self):
        state = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "high_score": self.high_score,
        }
        save_state(state)

    def run(self):
        while True:
            self.show_menu()
            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":
                print("아직 구현 전: 퀴즈 풀기")
            elif choice == "2":
                self.add_quiz()
            elif choice == "3":
                self.list_quizzes()
            elif choice == "4":
                print(f"최고 점수: {self.high_score}")
            elif choice == "5":
                self.save()
                print("프로그램을 종료합니다.")
                break
            else:
                print("올바른 번호를 입력하세요.")


    def add_quiz(self):
        question = input("문제를 입력하세요: ").strip()
        if not question:
            print("문제는 비워둘 수 없습니다.")
            return

        answer = input("정답을 입력하세요: ").strip()
        if not answer:
            print("정답은 비워둘 수 없습니다.")
            return

        new_quiz = Quiz(question, answer)
        self.quizzes.append(new_quiz)
        self.save()
        print("퀴즈가 추가되었습니다.")