from __future__ import annotations


def normalize_input(raw_value: str) -> str:
    return raw_value.strip()


def require_non_empty(raw_value: str, field_name: str = "입력") -> str:
    value = normalize_input(raw_value)
    if not value:
        raise ValueError(f"{field_name}은(는) 비워둘 수 없습니다.")
    return value


def parse_int(raw_value: str, field_name: str = "숫자") -> int:
    value = require_non_empty(raw_value, field_name)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{field_name}은(는) 숫자여야 합니다.") from exc


def validate_range(value: int, minimum: int, maximum: int, field_name: str = "숫자") -> int:
    if value < minimum or value > maximum:
        raise ValueError(f"{field_name}은(는) {minimum}부터 {maximum} 사이여야 합니다.")
    return value


def parse_int_in_range(
    raw_value: str,
    minimum: int,
    maximum: int,
    field_name: str = "숫자",
) -> int:
    numeric_value = parse_int(raw_value, field_name)
    return validate_range(numeric_value, minimum, maximum, field_name)
