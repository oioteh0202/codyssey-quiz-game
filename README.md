codyssey-quiz-game/
├─ .git
├─ .gitignore
├─ README.md
├─ main.py
├─ app/
│  ├─ __init__.py
│  ├─ controllers/
│  │  ├─ __init__.py
│  │  ├─ app_controller.py
│  │  └─ game_controller.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ question.py
│  │  ├─ question_bank.py
│  │  ├─ quiz_session.py
│  │  └─ state_repository.py
│  ├─ views/
│  │  ├─ __init__.py
│  │  ├─ menu_view.py
│  │  └─ game_view.py
│  └─ utils/
│     ├─ __init__.py
│     └─ validators.py
├─ data/
│  └─ questions.json
└─ tests/
   ├─ test_models.py
   ├─ test_controllers.py
   └─ test_state_repository.py