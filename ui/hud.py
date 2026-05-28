"""
HUD (heads-up display): счёт, жизни и оверлеи финальных экранов.
"""

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, YELLOW, RED, GREEN,
    PLAYER_LIVES,
)


class HUD:
    """
    Рисует игровой интерфейс поверх сцены:
    — счёт слева, иконки жизней справа (из спрайт-листа),
    — полупрозрачный оверлей при Game Over и Victory.
    """

    _FONT_LARGE  = 28
    _FONT_SMALL  = 20
    _MARGIN      = 10
    _HEART_SCALE = 0.40  # масштаб иконки жизни

    def __init__(
        self,
        heart_empty: pygame.Surface,
        heart_half:  pygame.Surface,
        heart_full:  pygame.Surface,
    ) -> None:
        # Шрифты создаются один раз в конструкторе
        self._font_large = pygame.font.SysFont("monospace", self._FONT_LARGE, bold=True)
        self._font_small = pygame.font.SysFont("monospace", self._FONT_SMALL)

        # Масштабируем иконки жизней один раз при инициализации
        self._hearts = {
            "full":  self._scale(heart_full),
            "half":  self._scale(heart_half),
            "empty": self._scale(heart_empty),
        }

    #  Отрисовка игрового интерфейса

    def draw(self, surface: pygame.Surface, score: int, lives: int) -> None:
        """Рисует счёт и иконки жизней на переданной поверхности."""
        # Счёт с ведущими нулями (6 цифр)
        score_surf = self._font_large.render(f"SCORE  {score:06d}", True, YELLOW)
        surface.blit(score_surf, (self._MARGIN, self._MARGIN))

        # Иконки жизней выровнены по правому краю
        heart_w = self._hearts["full"].get_width() + 4
        hx = SCREEN_WIDTH - PLAYER_LIVES * heart_w - self._MARGIN
        for i in range(PLAYER_LIVES):
            icon = self._hearts["full"] if i < lives else self._hearts["empty"]
            surface.blit(icon, (hx + i * heart_w, self._MARGIN))

    # Финальные оверлеи

    def draw_game_over(self, surface: pygame.Surface, score: int) -> None:
        self._draw_overlay(
            surface, title="GAME  OVER", title_colour=RED,
            lines=[f"Финальный счёт: {score:06d}", "", "R — рестарт", "Q — выход"],
        )

    def draw_victory(self, surface: pygame.Surface, score: int) -> None:
        self._draw_overlay(
            surface, title="ВЫ  ПОБЕДИЛИ!", title_colour=GREEN,
            lines=[f"Финальный счёт: {score:06d}", "", "R — сыграть ещё", "Q — выход"],
        )

    #  Вспомогательные методы

    def _draw_overlay(
        self,
        surface: pygame.Surface,
        title: str,
        title_colour: tuple,
        lines: list[str],
    ) -> None:
        """Рисует полупрозрачный тёмный экран с заголовком и строками текста."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 185))
        surface.blit(overlay, (0, 0))

        font_title = pygame.font.SysFont("monospace", 56, bold=True)
        title_surf = font_title.render(title, True, title_colour)
        surface.blit(
            title_surf,
            title_surf.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3),
        )

        for i, line in enumerate(lines):
            txt = self._font_small.render(line, True, WHITE)
            surface.blit(
                txt,
                txt.get_rect(
                    centerx=SCREEN_WIDTH // 2,
                    centery=SCREEN_HEIGHT // 2 + i * 34,
                ),
            )

    def _scale(self, surf: pygame.Surface) -> pygame.Surface:
        w = max(1, int(surf.get_width()  * self._HEART_SCALE))
        h = max(1, int(surf.get_height() * self._HEART_SCALE))
        return pygame.transform.scale(surf, (w, h))
