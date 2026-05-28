"""
Главный класс игры: инициализация, игровой цикл, стейт-машина.
Принимает сложность (difficulty) и применяет соответствующий пресет параметров.
После Game Over переходит в состояние ввода имени для таблицы рекордов.
"""

from __future__ import annotations

import sys
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    DARK_PURPLE, YELLOW, WHITE,
    ENEMY_ROW_TYPES, DIFFICULTY_PRESETS,
)
from entities.player    import Player
from entities.enemy     import Swarm
from entities.effects   import spawn_hit_particles
from ui.hud             import HUD

# Состояния игры
_STATE_PLAYING   = "playing"
_STATE_NEXT_WAVE = "next_wave"
_STATE_GAME_OVER = "game_over"

_NEXT_WAVE_DELAY = 2.5


class Game:
    """
    Игровой цикл одной сессии.
    difficulty — строка "easy" | "medium" | "expert", определяет пресет врагов.
    run() блокирует выполнение и возвращает финальный счёт после Game Over.
    """

    def __init__(self, screen: pygame.Surface, assets: dict, sounds: dict,
                 stars: list, difficulty: str = "medium") -> None:
        self._screen     = screen
        self._assets     = assets
        self._sounds     = sounds
        self._stars      = stars
        self._difficulty = difficulty
        self._clock      = pygame.time.Clock()

        # Применяем пресет сложности — перекладываем в атрибут для передачи в Swarm
        self._preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS["medium"])

        self._hud = HUD(
            heart_empty=self._assets["hearts"]["empty"],
            heart_half =self._assets["hearts"]["half"],
            heart_full =self._assets["hearts"]["full"],
        )
        self._explosion_frames = self._assets["explosions"]

        self._wave       = 1
        self._state      = _STATE_PLAYING
        self._wave_timer = 0.0

        self._setup_round(wave=1)

    # Точка входа 

    def run(self) -> int:
        """Запускает игровой цикл. Возвращает финальный счёт."""
        while True:
            dt = self._clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            result = self._handle_events()
            if result == "quit":
                pygame.quit()
                sys.exit()
            self._update(dt)
            self._draw()
            pygame.display.flip()

            # Когда игра закончена — возвращаем счёт в main.py
            if self._state == _STATE_GAME_OVER and self._game_over_done:
                return self._player.score

    # Инициализация раунда

    def _setup_round(self, wave: int) -> None:
        """Создаёт спрайты и Swarm для новой волны, сохраняя прогресс игрока."""
        self._wave           = wave
        self._game_over_done = False   # флаг: game_over уже «показан», можно выходить

        self._all_sprites    = pygame.sprite.Group()
        self._enemy_group    = pygame.sprite.Group()
        self._player_bullets = pygame.sprite.Group()
        self._enemy_bullets  = pygame.sprite.Group()
        self._effects_group  = pygame.sprite.Group()

        if wave == 1 or not hasattr(self, "_player_lives_carry"):
            self._player_lives_carry = None
            self._player_score_carry = 0

        self._player = Player(
            self._assets["player"],
            self._all_sprites,
            self._player_bullets,
        )
        if self._player_lives_carry is not None:
            self._player._lives = self._player_lives_carry
            self._player._score = self._player_score_carry

        self._all_sprites.add(self._player)

        sprite_data = {
            name: [surf]
            for name, surf in self._assets["enemies"].items()
            if name in ENEMY_ROW_TYPES.values()
        }

        self._swarm = Swarm(
            sprite_data      = sprite_data,
            all_sprites      = self._all_sprites,
            enemy_group      = self._enemy_group,
            bullets_group    = self._enemy_bullets,
            effects_group    = self._effects_group,
            explosion_frames = self._explosion_frames,
            wave             = wave,
            preset           = self._preset,   # передаём пресет сложности
        )
        self._state = _STATE_PLAYING

    # Обработка событий

    def _handle_events(self) -> str | None:
        """Обрабатывает события. Возвращает 'quit' при необходимости выхода."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return "quit"
                # Enter на экране Game Over — выходим из цикла (возврат счёта)
                if event.key == pygame.K_RETURN and self._state == _STATE_GAME_OVER:
                    self._game_over_done = True
        return None

    #Логика обновления 

    def _update(self, dt: float) -> None:
        if self._state == _STATE_GAME_OVER:
            self._effects_group.update(dt=dt)
            return

        if self._state == _STATE_NEXT_WAVE:
            self._effects_group.update(dt=dt)
            self._wave_timer -= dt
            if self._wave_timer <= 0:
                self._player_lives_carry = self._player.lives
                self._player_score_carry = self._player.score
                self._setup_round(wave=self._wave + 1)
            return

        self._all_sprites.update(dt=dt)
        self._swarm.update(dt)

        score_gained = self._swarm.handle_bullet_hits(self._player_bullets)
        if score_gained:
            self._player.add_score(score_gained)
            self._sounds["enemy_die"].play()

        self._handle_enemy_hits()
        self._check_game_state()

    def _handle_enemy_hits(self) -> None:
        if not self._player.alive_and_vulnerable:
            return
        hit_by_bullet = pygame.sprite.spritecollide(
            self._player, self._enemy_bullets, dokill=True
        )
        hit_by_enemy = pygame.sprite.spritecollide(
            self._player, self._enemy_group, dokill=False
        )
        if hit_by_bullet or hit_by_enemy:
            self._player.take_hit()
            self._sounds["player_hit"].play()
            spawn_hit_particles(
                [self._all_sprites, self._effects_group],
                self._player.rect.centerx,
                self._player.rect.centery,
                colour=(80, 180, 255),
                count=12,
            )

    def _check_game_state(self) -> None:
        if self._player.lives <= 0:
            self._state = _STATE_GAME_OVER
            self._sounds["player_hit"].play()
            return
        if self._swarm.has_landed:
            self._state = _STATE_GAME_OVER
            return
        if self._swarm.all_dead:
            self._state      = _STATE_NEXT_WAVE
            self._wave_timer = _NEXT_WAVE_DELAY
            self._sounds["victory"].play()

    # Отрисовка 

    def _draw(self) -> None:
        self._screen.fill(DARK_PURPLE)
        for x, y, brightness in self._stars:
            self._screen.set_at((x, y), (brightness, brightness, brightness))

        for sprite in self._all_sprites:
            if isinstance(sprite, Player):
                sprite.draw(self._screen)
            else:
                self._screen.blit(sprite.image, sprite.rect)

        self._hud.draw(self._screen, self._player.score, self._player.lives)
        self._draw_wave_label()

        if self._state == _STATE_GAME_OVER:
            self._draw_game_over_overlay()
        elif self._state == _STATE_NEXT_WAVE:
            self._draw_next_wave_banner()

    def _draw_wave_label(self) -> None:
        font = pygame.font.SysFont("monospace", 18)
        surf = font.render(f"WAVE  {self._wave}", True, YELLOW)
        self._screen.blit(surf, (10, SCREEN_HEIGHT - surf.get_height() - 10))

    def _draw_game_over_overlay(self) -> None:
        """Game Over — минималистичный оверлей, ввод имени будет в отдельном экране."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 10, 160))
        self._screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("monospace", 56, bold=True)
        font_sm  = pygame.font.SysFont("monospace", 22)

        title = font_big.render("GAME  OVER", True, (220, 30, 30))
        sub   = font_sm.render("Enter — продолжить", True, WHITE)

        self._screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 - 40))
        self._screen.blit(sub,   sub.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 + 40))

    def _draw_next_wave_banner(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 160))
        self._screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("monospace", 52, bold=True)
        font_sm  = pygame.font.SysFont("monospace", 22)
        title    = font_big.render(f"ВОЛНА  {self._wave + 1}", True, YELLOW)
        sub      = font_sm.render("Приготовься...", True, WHITE)

        self._screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 - 30))
        self._screen.blit(sub,   sub.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 + 40))
