import json
import os

STATE_FILE = "state.json"


def default_state():
    return {
        "quizzes": [],
        "high_score": 0,
    }


def load_state():
    if not os.path.exists(STATE_FILE):
        return default_state()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return default_state()

        if "quizzes" not in data or "high_score" not in data:
            return default_state()

        if not isinstance(data["quizzes"], list):
            return default_state()

        if not isinstance(data["high_score"], int):
            return default_state()

        return data

    except (json.JSONDecodeError, OSError):
        return default_state()


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)