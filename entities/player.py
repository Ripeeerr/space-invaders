"""
Корабль игрока: движение, стрельба, неуязвимость с миганием.
Хитбокс меньше видимого спрайта (PLAYER_HITBOX_SHRINK).
"""

import pygame
from settings import (
    SCREEN_WIDTH,
    PLAYER_SPEED, PLAYER_LIVES,
    PLAYER_SHOOT_DELAY, PLAYER_SCALE,
    PLAYER_HITBOX_SHRINK,
    PLAYER_BLINK_TIME, PLAYER_BLINK_RATE,
)
from entities.bullet import PlayerBullet


class Player(pygame.sprite.Sprite):
    """
    Управляемый игроком корабль.
    Движение: A/D или стрелки. Выстрел: Пробел.
    После попадания — неуязвим PLAYER_BLINK_TIME секунд и мигает.
    Хитбокс составляет PLAYER_HITBOX_SHRINK от размера спрайта — уменьшен
    для честного геймплея при широком спрайте корабля.
    """

    def __init__(
        self,
        sprite: pygame.Surface,
        all_sprites: pygame.sprite.Group,
        bullets_group: pygame.sprite.Group,
    ) -> None:
        super().__init__()

        # Масштабируем спрайт и сохраняем эталон
        w = max(1, int(sprite.get_width()  * PLAYER_SCALE))
        h = max(1, int(sprite.get_height() * PLAYER_SCALE))
        self._base_image = pygame.transform.scale(sprite, (w, h))
        self.image = self._base_image.copy()

        # Визуальный rect — для отрисовки, расположен внизу по центру
        self._vis_rect = self.image.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=pygame.display.get_surface().get_height() - 20,
        )

        # Хитбокс — уменьшенный прямоугольник внутри спрайта, для коллизий
        # Он меньше видимого спрайта на (1 - PLAYER_HITBOX_SHRINK) с каждой стороны
        hw = max(4, int(w * PLAYER_HITBOX_SHRINK))
        hh = max(4, int(h * PLAYER_HITBOX_SHRINK))
        self.rect = pygame.Rect(0, 0, hw, hh)
        self.rect.center = self._vis_rect.center

        self._x = float(self._vis_rect.x)

        self._lives = PLAYER_LIVES
        self._score = 0
        self._shoot_cooldown = 0.0

        # Состояние неуязвимости и мигания
        self._invincible  = False
        self._inv_timer   = 0.0
        self._blink_timer = 0.0
        self._visible     = True

        self._all_sprites   = all_sprites
        self._bullets_group = bullets_group

    # Свойства 

    @property
    def lives(self) -> int:
        return self._lives

    @property
    def score(self) -> int:
        return self._score

    @property
    def alive_and_vulnerable(self) -> bool:
        return not self._invincible

    # Публичные методы 

    def add_score(self, points: int) -> None:
        self._score += points

    def take_hit(self) -> None:
        """Вызывается при попадании пули или касании врага."""
        if self._invincible:
            return
        self._lives -= 1
        self._invincible  = True
        self._inv_timer   = 0.0
        self._blink_timer = 0.0

    #Обновление каждый кадр 

    def update(self, dt: float, **_) -> None:
        keys = pygame.key.get_pressed()
        self._handle_movement(keys, dt)
        self._handle_shooting(keys, dt)
        self._handle_invincibility(dt)

        # Синхронизируем хитбокс с визуальным положением
        self.rect.center = self._vis_rect.center

    # Вспомогательные методы

    def _handle_movement(self, keys, dt: float) -> None:
        """Горизонтальное движение с ограничением по краям экрана."""
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1

        self._x += dx * PLAYER_SPEED * dt
        half_w = self._vis_rect.width / 2
        self._x = max(half_w, min(SCREEN_WIDTH - half_w, self._x))
        self._vis_rect.x = int(self._x)

    def _handle_shooting(self, keys, dt: float) -> None:
        """Создаёт пулю при нажатии Пробела с учётом кулдауна."""
        self._shoot_cooldown = max(0.0, self._shoot_cooldown - dt)
        if keys[pygame.K_SPACE] and self._shoot_cooldown == 0.0:
            bullet = PlayerBullet(self._vis_rect.centerx, self._vis_rect.top)
            self._all_sprites.add(bullet)
            self._bullets_group.add(bullet)
            self._shoot_cooldown = PLAYER_SHOOT_DELAY

    def _handle_invincibility(self, dt: float) -> None:
        """Мигание и снятие неуязвимости по истечении таймера."""
        if not self._invincible:
            self.image = self._base_image
            return

        self._inv_timer   += dt
        self._blink_timer += dt

        if self._blink_timer >= PLAYER_BLINK_RATE:
            self._blink_timer -= PLAYER_BLINK_RATE
            self._visible = not self._visible

        if self._visible:
            self.image = self._base_image
        else:
            blank = self._base_image.copy()
            blank.set_alpha(0)
            self.image = blank

        if self._inv_timer >= PLAYER_BLINK_TIME:
            self._invincible = False
            self._visible    = True
            self.image       = self._base_image

    #Отрисовка

    def draw_hitbox(self, surface: pygame.Surface) -> None:
        """Отладочный метод: рисует хитбокс красным контуром."""
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

    def draw(self, surface: pygame.Surface) -> None:
        """Рисует спрайт корабля по визуальному rect (не хитбоксу)."""
        if self.image.get_alpha() != 0:
            surface.blit(self.image, self._vis_rect)
