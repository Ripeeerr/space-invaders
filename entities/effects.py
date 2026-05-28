"""
Визуальные эффекты: взрывы на основе спрайтов и частицы при попадании.
"""

import math
import random
import pygame

from settings import (
    EXPLOSION_DURATION,
    HIT_PARTICLE_COUNT, HIT_PARTICLE_SPEED, HIT_PARTICLE_LIFE,
)


class Explosion(pygame.sprite.Sprite):
    """
    Анимированный взрыв из нескольких статичных кадров (explosion1 → 2 → 3).
    Каждый кадр показывается EXPLOSION_DURATION секунд, затем спрайт удаляется.
    Кадры масштабируются под размер взрываемого объекта через параметр scale.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        cx: int,
        cy: int,
        scale: float = 1.0,
    ) -> None:
        super().__init__()

        # Масштабируем все кадры если задан scale
        if scale != 1.0:
            self._frames = [
                pygame.transform.scale(
                    f,
                    (max(1, int(f.get_width()  * scale)),
                     max(1, int(f.get_height() * scale)))
                )
                for f in frames
            ]
        else:
            self._frames = list(frames)

        self._timer     = 0.0
        self._frame_idx = 0
        self.image = self._frames[0]
        self.rect  = self.image.get_rect(center=(cx, cy))

    def update(self, dt: float, **_) -> None:
        self._timer += dt

        # Вычисляем индекс текущего кадра по прошедшему времени
        self._frame_idx = min(
            int(self._timer / EXPLOSION_DURATION),
            len(self._frames) - 1,
        )
        self.image = self._frames[self._frame_idx]
        self.rect  = self.image.get_rect(center=self.rect.center)

        # Когда все кадры отыграли — удаляем спрайт
        if self._timer >= EXPLOSION_DURATION * len(self._frames):
            self.kill()


class Particle(pygame.sprite.Sprite):
    """
    Одиночная частица (квадрат 4×4 px), разлетающаяся от точки попадания.
    Плавно затухает по мере приближения к концу жизни.
    """

    def __init__(self, cx: int, cy: int, colour: tuple) -> None:
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.image.fill(colour)
        self.rect  = self.image.get_rect(center=(cx, cy))

        # Случайный угол и скорость разлёта
        angle = random.uniform(0, math.tau)
        speed = random.uniform(HIT_PARTICLE_SPEED * 0.5, HIT_PARTICLE_SPEED)
        self._vx     = math.cos(angle) * speed
        self._vy     = math.sin(angle) * speed
        self._x      = float(cx)
        self._y      = float(cy)
        self._life   = HIT_PARTICLE_LIFE
        self._age    = 0.0
        self._colour = colour

    def update(self, dt: float, **_) -> None:
        self._age += dt
        if self._age >= self._life:
            self.kill()
            return

        # Линейное движение и плавное затухание прозрачности
        self._x += self._vx * dt
        self._y += self._vy * dt
        self.rect.center = (int(self._x), int(self._y))
        alpha = int(255 * (1.0 - self._age / self._life))
        self.image.fill((*self._colour[:3], alpha))


def spawn_hit_particles(
    groups: list,
    cx: int,
    cy: int,
    colour: tuple = (255, 200, 50),
    count: int = HIT_PARTICLE_COUNT,
) -> None:
    """Создаёт count частиц в точке (cx, cy) и добавляет их в переданные группы."""
    for _ in range(count):
        p = Particle(cx, cy, colour)
        for g in groups:
            g.add(p)
