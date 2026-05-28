"""
Загрузчик ассетов.
каждый спрайт — отдельный PNG с уже прозрачным фоном,
поэтому загрузка сводится к pygame.image.load + масштабирование.
"""

from pathlib import Path
import pygame

from settings import ASSET_PATHS, ENEMY_SCALE, PLAYER_SCALE


def load_assets() -> dict:
    """
    Загружает все игровые ассеты из отдельных PNG-файлов.

    Возвращает словарь:
        {
            "enemies":    { "alien1": Surface, "alien2": Surface, ... },
            "player":     Surface,
            "explosions": [Surface, Surface, Surface],   # маленький → большой
            "hearts":     { "full": Surface, "half": Surface, "empty": Surface },
        }

    Спрайты врагов и корабля масштабируются согласно ENEMY_SCALE / PLAYER_SCALE.
    Взрывы и сердечки загружаются в оригинальном размере
    (масштабирование при необходимости делается на месте использования).
    """
    assets: dict = {}

    # Загружаем спрайты врагов и сразу масштабируем
    assets["enemies"] = {}
    for name, path in ASSET_PATHS["enemies"].items():
        surf = _load(path)
        assets["enemies"][name] = _scale(surf, ENEMY_SCALE)

    # Корабль игрока
    assets["player"] = _scale(_load(ASSET_PATHS["player"]), PLAYER_SCALE)

    # Взрывы — список из трёх поверхностей [маленький, средний, большой]
    assets["explosions"] = [_load(p) for p in ASSET_PATHS["explosions"]]

    # Иконки жизней
    assets["hearts"] = {
        key: _load(path)
        for key, path in ASSET_PATHS["hearts"].items()
    }

    return assets


# Вспомогательные функции

def _load(path: str | Path) -> pygame.Surface:
    """
    Загружает PNG с прозрачным фоном.
    convert_alpha() оптимизирует поверхность для быстрой отрисовки с альфой.
    """
    return pygame.image.load(str(path)).convert_alpha()


def _scale(surf: pygame.Surface, scale: float) -> pygame.Surface:
    """
    Масштабирует поверхность без сглаживания (сохраняет пиксель-арт стиль).
    max(1, ...) защищает от нулевого размера при очень маленьком scale.
    """
    if scale == 1.0:
        return surf
    w = max(1, int(surf.get_width()  * scale))
    h = max(1, int(surf.get_height() * scale))
    return pygame.transform.scale(surf, (w, h))
