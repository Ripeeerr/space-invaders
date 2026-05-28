"""
Таблица рекордов: загрузка, сохранение и обновление записей.
Данные хранятся в файле records.json рядом с main.py.
Формат записи: { "name": str, "difficulty": str, "score": int }

Правило обновления:
— Если игрок с таким именем уже есть И его новый счёт БОЛЬШЕ — обновляем.
— Если меньше или равен — оставляем старый.
— Новое имя — добавляем.
Таблица всегда отсортирована по убыванию счёта.
"""

from __future__ import annotations
import json
from pathlib import Path

_RECORDS_FILE = Path("records.json")
_MAX_RECORDS  = 100   # максимальное число хранимых записей


def load_records() -> list[dict]:
    """Читает records.json и возвращает список словарей. Если файла нет — пустой список."""
    if not _RECORDS_FILE.exists():
        return []
    try:
        with _RECORDS_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
        # Проверяем что данные — список словарей с нужными ключами
        if isinstance(data, list):
            return [r for r in data if {"name", "difficulty", "score"} <= r.keys()]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_record(name: str, difficulty: str, score: int) -> None:
    """
    Добавляет или обновляет запись в таблице рекордов.
    Имя сравнивается без учёта регистра, чтобы «Alice» и «alice» считались одним игроком.
    """
    if not name:
        return

    records = load_records()

    # Ищем существующую запись по имени (без учёта регистра)
    name_lower = name.strip().lower()
    existing   = next(
        (r for r in records if r["name"].lower() == name_lower),
        None,
    )

    if existing is None:
        # Новое имя — добавляем запись
        records.append({"name": name.strip(), "difficulty": difficulty, "score": score})
    elif score > existing["score"]:
        # Тот же игрок, новый рекорд — обновляем
        existing["score"]      = score
        existing["difficulty"] = difficulty

    # Сортируем по убыванию счёта и обрезаем лишнее
    records.sort(key=lambda r: r["score"], reverse=True)
    records = records[:_MAX_RECORDS]

    with _RECORDS_FILE.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def get_top(n: int = 10) -> list[tuple[str, str, int]]:
    """
    Возвращает топ-N записей в виде списка кортежей (имя, сложность, счёт).
    Удобно передавать напрямую в LeaderboardScreen.
    """
    records = load_records()
    return [(r["name"], r["difficulty"], r["score"]) for r in records[:n]]
