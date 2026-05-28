"""
Точка входа. Управляет потоком экранов:
  Главное меню → Выбор сложности → Игра → Ввод имени → (снова меню)
                ↓
           Таблица рекордов → Главное меню
"""

import random
import sys
import pygame

from settings         import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
from core.sprite_loader import load_assets
from core.sounds        import load_sounds
from core.game          import Game
from core.leaderboard   import save_record, get_top
from ui.menu            import MainMenu, DifficultyMenu, NameInputScreen, LeaderboardScreen


def _make_stars(count: int = 120) -> list[tuple[int, int, int]]:
    """Генерирует статичное звёздное поле, общее для всех экранов."""
    return [
        (
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.randint(80, 220),
        )
        for _ in range(count)
    ]


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Ресурсы загружаются один раз и передаются во все экраны
    assets = load_assets()
    sounds = load_sounds()
    stars  = _make_stars()

    while True:
        # Главное меню 
        action = MainMenu(screen, stars).run()

        if action == "quit":
            pygame.quit()
            sys.exit()

        if action == "leaderboard":
            LeaderboardScreen(screen, stars, get_top(10)).run()
            continue   # вернуться в главное меню

        # action == "play" → выбор сложности
        diff = DifficultyMenu(screen, stars).run()
        if diff == "back":
            continue   # вернуться в главное меню

        #Игровой цикл 
        # Game.run() блокирует и возвращает финальный счёт
        score = Game(screen, assets, sounds, stars, difficulty=diff).run()

        # Ввод имени и сохранение рекорда 
        name = NameInputScreen(screen, stars, score).run()
        if name:
            save_record(name, diff, score)

        # Показать таблицу рекордов сразу после игры
        LeaderboardScreen(screen, stars, get_top(10)).run()
        # Далее цикл вернётся в главное меню


if __name__ == "__main__":
    main()
