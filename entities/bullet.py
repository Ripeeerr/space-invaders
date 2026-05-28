"""
Пули игрока и врагов.
"""

import pygame
from settings import (
    PLAYER_BULLET_SPEED, ENEMY_BULLET_SPEED,
    BULLET_WIDTH, BULLET_HEIGHT,
    SCREEN_HEIGHT,
)


class PlayerBullet(pygame.sprite.Sprite):
    """Пуля игрока — летит вверх, рисуется как голубой лазер с сердцевиной."""

    def __init__(self, cx: int, cy: int) -> None:
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        # Внешний слой (голубой) и яркая сердцевина (белёсый)
        pygame.draw.rect(self.image, (100, 220, 255), (1, 0, 2, BULLET_HEIGHT))
        pygame.draw.rect(self.image, (200, 240, 255), (1, 2, 2, BULLET_HEIGHT - 4))
        self.rect = self.image.get_rect(centerx=cx, bottom=cy)
        self._y   = float(self.rect.y)

    def update(self, dt: float, **_) -> None:
        self._y -= PLAYER_BULLET_SPEED * dt
        self.rect.y = int(self._y)
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    """Пуля врага — летит вниз, рисуется как красно-оранжевый разряд."""

    def __init__(self, cx: int, cy: int) -> None:
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        # Внешний слой (красный) и оранжевая сердцевина
        pygame.draw.rect(self.image, (255,  60,  60), (1, 0, 2, BULLET_HEIGHT))
        pygame.draw.rect(self.image, (255, 180,  80), (1, 2, 2, BULLET_HEIGHT - 4))
        self.rect = self.image.get_rect(centerx=cx, top=cy)
        self._y   = float(self.rect.y)

    def update(self, dt: float, **_) -> None:
        self._y += ENEMY_BULLET_SPEED * dt
        self.rect.y = int(self._y)
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()
