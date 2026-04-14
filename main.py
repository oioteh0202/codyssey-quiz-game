from app.controllers.app_controller import AppController


def main() -> None:
    app_controller = AppController()
    try:
        app_controller.run()
    except Exception:
        print("오류가 발생해 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
