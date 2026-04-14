from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StateRepository:
    def __init__(self, state_path: str | Path = "state.json") -> None:
        self._state_path = Path(state_path)

    def save(self, state: dict[str, Any]) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        with self._state_path.open("w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

    def load(self) -> dict[str, Any]:
        if not self._state_path.exists():
            raise FileNotFoundError("저장 파일이 없습니다.")

        try:
            with self._state_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("저장 파일이 손상되었습니다.") from error
        except OSError as error:
            raise ValueError("저장 파일을 읽을 수 없습니다.") from error

        if not isinstance(data, dict):
            raise ValueError("저장 데이터 형식이 올바르지 않습니다.")
        return data
