"""
Звуковая подсистема.
Все звуки генерируются программно из математических волн (NumPy + pygame.sndarray).
Внешние аудиофайлы не нужны — проект полностью самодостаточен.
"""

import numpy as np
import pygame

_SAMPLE_RATE = 22050  # частота дискретизации, сэмплов в секунду


def _make_sound(
    freq_envelope: list[tuple[float, float]],
    volume: float = 0.4,
    wave: str = "square",
) -> pygame.mixer.Sound:
    """
    Генерирует Sound из набора сегментов (частота Гц, длительность сек).
    Типы волн: 'square' (резкий), 'sawtooth' (грубый), 'sine' (плавный).
    """
    parts = []
    for freq, duration in freq_envelope:
        n      = int(_SAMPLE_RATE * duration)
        t      = np.linspace(0, duration, n, endpoint=False)

        # Формирование волны выбранного типа
        if wave == "square":
            chunk = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave == "sawtooth":
            chunk = 2 * (t * freq - np.floor(t * freq + 0.5))
        else:
            chunk = np.sin(2 * np.pi * freq * t)

        # Короткое затухание в конце сегмента — убирает щелчок
        fade = np.linspace(1, 0, min(n, _SAMPLE_RATE // 20))
        chunk[-len(fade):] *= fade
        parts.append(chunk)

    # Объединяем сегменты, масштабируем к int16 и делаем стерео
    arr    = np.concatenate(parts)
    arr    = (arr * volume * 32767).astype(np.int16)
    stereo = np.column_stack([arr, arr])
    return pygame.sndarray.make_sound(stereo)


def load_sounds() -> dict[str, pygame.mixer.Sound]:
    """Создаёт и возвращает словарь всех игровых звуков."""
    pygame.mixer.init(frequency=_SAMPLE_RATE, size=-16, channels=2, buffer=512)

    return {
        # Выстрел игрока: три нисходящих ноты, резкая прямоугольная волна
        "shoot": _make_sound(
            [(880, 0.04), (660, 0.04), (440, 0.03)], volume=0.25, wave="square"
        ),
        # Гибель врага: низкий нисходящий шум, пилообразная волна
        "enemy_die": _make_sound(
            [(300, 0.05), (200, 0.05), (100, 0.08)], volume=0.35, wave="sawtooth"
        ),
        # Попадание по игроку: низкий гулкий удар
        "player_hit": _make_sound(
            [(160, 0.08), (100, 0.10), (60, 0.12)], volume=0.45, wave="square"
        ),
        # Маршевый ритм (не используется активно, точка расширения)
        "march": _make_sound(
            [(160, 0.06), (130, 0.06), (110, 0.06), (90, 0.06)], volume=0.20, wave="square"
        ),
        # Джингл победы: восходящий аккорд синусоидой
        "victory": _make_sound(
            [(440, 0.1), (550, 0.1), (660, 0.1), (880, 0.25)], volume=0.35, wave="sine"
        ),
    }
