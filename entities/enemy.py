"""
Сущности врагов и контроллер роя (Swarm).
Enemy — один инопланетянин со статичным спрайтом.
Swarm — управляет сеткой: движение, отскоки, ускорение, стрельба очередью.
Параметры стрельбы и скорости берутся из пресета сложности (preset dict).
"""

import random
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_ROWS, ENEMY_COLS,
    ENEMY_H_SPACING, ENEMY_V_SPACING, ENEMY_START_Y,
    ENEMY_STEP_X, ENEMY_STEP_Y,
    ENEMY_STEP_INTERVAL,
    ENEMY_SCALE, ENEMY_ANIM_RATE, ENEMY_ROW_TYPES, ENEMY_ROW_SCORES,
)
from entities.bullet import EnemyBullet
from entities.effects import Explosion, spawn_hit_particles


class Enemy(pygame.sprite.Sprite):
    """Один инопланетянин. Поддерживает список кадров (достаточно одного для статики)."""

    def __init__(
        self,
        frames: list[pygame.Surface],
        row: int,
        col: int,
        enemy_type: str,
    ) -> None:
        super().__init__()

        # Масштабируем все кадры при создании
        self._frames = [
            pygame.transform.scale(
                f,
                (max(1, int(f.get_width()  * ENEMY_SCALE)),
                 max(1, int(f.get_height() * ENEMY_SCALE))),
            )
            for f in frames
        ]
        self._frame_idx  = 0
        self.image       = self._frames[0]
        self.rect        = self.image.get_rect()
        self.row         = row
        self.col         = col
        self.enemy_type  = enemy_type
        self.score_value = ENEMY_ROW_SCORES[enemy_type]

    def set_frame(self, idx: int) -> None:
        """Переключить кадр анимации (безопасно работает и с одним кадром)."""
        self._frame_idx = idx % len(self._frames)
        self.image      = self._frames[self._frame_idx]


class Swarm:
    """
    Контроллер роя врагов.
    Принимает preset — словарь с параметрами сложности из DIFFICULTY_PRESETS.
    Стрельба очередью: раз в queue_delay секунд стреляет самый нижний враг
    случайной колонны — никакого одновременного залпа.
    """

    def __init__(
        self,
        sprite_data: dict,
        all_sprites: pygame.sprite.Group,
        enemy_group: pygame.sprite.Group,
        bullets_group: pygame.sprite.Group,
        effects_group: pygame.sprite.Group,
        explosion_frames: list[pygame.Surface],
        wave: int = 1,
        preset: dict | None = None,
    ) -> None:
        self._all_sprites      = all_sprites
        self._enemy_group      = enemy_group
        self._bullets_group    = bullets_group
        self._effects_group    = effects_group
        self._explosion_frames = explosion_frames
        self._wave             = wave

        # Читаем параметры из пресета сложности (с запасными значениями по умолчанию)
        p = preset or {}
        self._shoot_min    = p.get("enemy_shoot_interval_min", 1.8)
        self._shoot_max    = p.get("enemy_shoot_interval_max", 4.0)
        self._max_bullets  = p.get("enemy_max_bullets",        3)
        self._queue_delay  = p.get("enemy_shoot_queue_delay",  0.35)
        self._wave_bonus   = p.get("wave_speed_bonus",         0.08)
        self._wave_min     = p.get("wave_min_step",            0.12)

        # Интервал шага уменьшается с каждой волной (параметр из пресета)
        raw_interval        = ENEMY_STEP_INTERVAL - (wave - 1) * self._wave_bonus
        self._step_interval = max(self._wave_min, raw_interval)
        self._step_timer    = 0.0
        self._anim_timer    = 0.0
        self._anim_frame    = 0
        self._direction     = 1  # +1 = вправо, -1 = влево

        # Первый выстрел через случайный интервал (не сразу при старте)
        self._queue_timer = random.uniform(self._shoot_min, self._shoot_max)

        self._build_grid(sprite_data)

    # Публичный интерфейс

    @property
    def all_dead(self) -> bool:
        return len(self._enemy_group) == 0

    @property
    def has_landed(self) -> bool:
        """True, если хоть один враг достиг нижней части экрана."""
        for e in self._enemy_group:
            if e.rect.bottom >= SCREEN_HEIGHT - 80:
                return True
        return False

    def update(self, dt: float) -> None:
        self._update_animation(dt)
        self._update_step(dt)
        self._update_shooting(dt)

    #Обработка столкновений 

    def handle_bullet_hits(self, player_bullets: pygame.sprite.Group) -> int:
        """Проверяет столкновения пуль игрока с врагами. Возвращает очки."""
        total = 0
        hits  = pygame.sprite.groupcollide(
            self._enemy_group, player_bullets,
            dokilla=True, dokillb=True,
        )
        for enemy in hits:
            total += enemy.score_value
            cx, cy = enemy.rect.center
            exp = Explosion(self._explosion_frames, cx, cy, scale=0.45)
            self._all_sprites.add(exp)
            self._effects_group.add(exp)
            spawn_hit_particles(
                [self._all_sprites, self._effects_group],
                cx, cy, colour=(255, 180, 50),
            )
        return total

    #Вспомогательные методы 

    def _build_grid(self, sprite_data: dict) -> None:
        """
        Создаёт сетку врагов, центрированную по экрану.
        Ключ в sprite_data — имя типа из ENEMY_ROW_TYPES (например 'alien1'),
        БЕЗ префикса 'enemy_' — это исправляет ошибку KeyError из предыдущей версии.
        """
        total_width = (ENEMY_COLS - 1) * ENEMY_H_SPACING
        start_x     = (SCREEN_WIDTH - total_width) // 2

        for row in range(ENEMY_ROWS):
            enemy_type = ENEMY_ROW_TYPES[row]
            frames     = sprite_data[enemy_type]   # ключ без префикса "enemy_"
            for col in range(ENEMY_COLS):
                e = Enemy(frames, row, col, enemy_type)
                e.rect.centerx = start_x + col * ENEMY_H_SPACING
                e.rect.centery = ENEMY_START_Y + row * ENEMY_V_SPACING
                self._all_sprites.add(e)
                self._enemy_group.add(e)

    def _update_animation(self, dt: float) -> None:
        """Синхронно переключает кадр анимации у всех врагов (для статики — no-op)."""
        self._anim_timer += dt
        if self._anim_timer >= ENEMY_ANIM_RATE:
            self._anim_timer -= ENEMY_ANIM_RATE
            self._anim_frame = 1 - self._anim_frame
            for e in self._enemy_group:
                e.set_frame(self._anim_frame)

    def _update_step(self, dt: float) -> None:
        """
        Горизонтальное движение дискретными шагами.
        При достижении края — разворот и опускание вниз.
        Интервал сокращается по мере гибели врагов (ускорение).
        """
        self._step_timer += dt
        if self._step_timer < self._step_interval:
            return
        self._step_timer -= self._step_interval

        if not self._enemy_group:
            return

        leftest  = min(e.rect.left  for e in self._enemy_group)
        rightest = max(e.rect.right for e in self._enemy_group)
        next_l   = leftest  + self._direction * ENEMY_STEP_X
        next_r   = rightest + self._direction * ENEMY_STEP_X

        if next_r > SCREEN_WIDTH - 10 or next_l < 10:
            self._direction *= -1
            for e in self._enemy_group:
                e.rect.y += ENEMY_STEP_Y
        else:
            for e in self._enemy_group:
                e.rect.x += self._direction * ENEMY_STEP_X

        # Ускорение: чем меньше врагов, тем короче интервал (до wave_min)
        fraction = len(self._enemy_group) / (ENEMY_ROWS * ENEMY_COLS)
        self._step_interval = max(
            self._wave_min,
            self._wave_min + (self._step_interval - self._wave_min) * fraction,
        )

    def _update_shooting(self, dt: float) -> None:
        """
        Стрельба очередью по колоннам.
        Раз в _queue_delay секунд — случайная колонна, нижний враг стреляет.
        Новые пули не создаются если достигнут лимит _max_bullets.
        """
        self._queue_timer -= dt
        if self._queue_timer > 0:
            return

        self._queue_timer = self._queue_delay

        if len(self._bullets_group) >= self._max_bullets:
            self._queue_timer = random.uniform(0.3, 0.7)
            return

        # Строим карту колонн: номер колонны → список живых врагов в ней
        cols: dict[int, list[Enemy]] = {}
        for e in self._enemy_group:
            cols.setdefault(e.col, []).append(e)

        if not cols:
            return

        # Случайная колонна, нижний враг в ней
        chosen_col = random.choice(list(cols.keys()))
        shooter    = max(cols[chosen_col], key=lambda e: e.rect.bottom)

        bullet = EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
        self._all_sprites.add(bullet)
        self._bullets_group.add(bullet)

        # Следующий тик через случайный интервал из пресета
        self._queue_timer = random.uniform(self._shoot_min, self._shoot_max)
