class QuizGame:
    def run(self):
        while True:
            print("\n==== 퀴즈 게임 ====")
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 추가")
            print("3. 퀴즈 목록")
            print("4. 점수 확인")
            print("5. 종료")

            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":
                print("아직 구현 전: 퀴즈 풀기")
            elif choice == "2":
                print("아직 구현 전: 퀴즈 추가")
            elif choice == "3":
                print("아직 구현 전: 퀴즈 목록")
            elif choice == "4":
                print("아직 구현 전: 점수 확인")
            elif choice == "5":
                print("프로그램을 종료합니다.")
                break
            else:
                print("올바른 번호를 입력하세요.")


if __name__ == "__main__":
    game = QuizGame()
    game.run()
