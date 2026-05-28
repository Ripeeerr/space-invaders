"""
Экраны вне игрового цикла:
— главное меню (Play, Leaderboard, Quit)
— выбор сложности
— ввод имени после поражения
— таблица рекордов
"""

from __future__ import annotations
import pygame
from settings import SCREEN_WIDTH, DARK_PURPLE, WHITE, YELLOW, RED, GREEN, CYAN


#Вспомогательный класс кнопки

class _Button:
    """Простая текстовая кнопка с подсветкой при наведении."""

    _FONT_SIZE = 32

    def __init__(self, text: str, centerx: int, centery: int) -> None:
        self._text   = text
        self._font   = pygame.font.SysFont("monospace", self._FONT_SIZE, bold=True)
        self._rect   = pygame.Rect(0, 0, 340, 52)
        self._rect.center = (centerx, centery)

    def draw(self, surface: pygame.Surface) -> None:
        hovered = self._rect.collidepoint(pygame.mouse.get_pos())
        colour  = YELLOW if hovered else WHITE

        # Фоновый прямоугольник кнопки
        bg_colour = (50, 50, 80) if hovered else (25, 25, 50)
        pygame.draw.rect(surface, bg_colour,   self._rect, border_radius=8)
        pygame.draw.rect(surface, colour,      self._rect, width=2, border_radius=8)

        label = self._font.render(self._text, True, colour)
        surface.blit(label, label.get_rect(center=self._rect.center))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Возвращает True если по кнопке кликнули левой кнопкой мыши."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self._rect.collidepoint(event.pos)
        )


#  Главное меню 

class MainMenu:
    """
    Главное меню: Play, Leaderboard, Quit.
    run() блокирует выполнение и возвращает строку-действие:
      "play"        — игрок нажал Play (следующий шаг — выбор сложности)
      "leaderboard" — показать таблицу рекордов
      "quit"        — выход
    """

    def __init__(self, screen: pygame.Surface, stars: list) -> None:
        self._screen = screen
        self._stars  = stars
        self._clock  = pygame.time.Clock()

        cx = SCREEN_WIDTH // 2
        self._btn_play   = _Button("ИГРАТЬ",        cx, 320)
        self._btn_leader = _Button("РЕКОРДЫ",      cx, 390)
        self._btn_quit   = _Button("ВЫХОД",          cx, 460)

        self._font_title = pygame.font.SysFont("monospace", 64, bold=True)
        self._font_sub   = pygame.font.SysFont("monospace", 20)

    def run(self) -> str:
        while True:
            self._clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if self._btn_play.is_clicked(event):
                    return "play"
                if self._btn_leader.is_clicked(event):
                    return "leaderboard"
                if self._btn_quit.is_clicked(event):
                    return "quit"

            self._draw()

    def _draw(self) -> None:
        self._screen.fill(DARK_PURPLE)
        for x, y, b in self._stars:
            self._screen.set_at((x, y), (b, b, b))

        # Заголовок
        title = self._font_title.render("SPACE INVADERS", True, YELLOW)
        self._screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=210))

        sub = self._font_sub.render("пиксельная аркада", True, CYAN)
        self._screen.blit(sub, sub.get_rect(centerx=SCREEN_WIDTH // 2, centery=270))

        self._btn_play.draw(self._screen)
        self._btn_leader.draw(self._screen)
        self._btn_quit.draw(self._screen)

        pygame.display.flip()


#Выбор сложности 

class DifficultyMenu:
    """
    Экран выбора сложности.
    run() возвращает строку: "easy" | "medium" | "expert" | "back"
    """

    def __init__(self, screen: pygame.Surface, stars: list) -> None:
        self._screen = screen
        self._stars  = stars
        self._clock  = pygame.time.Clock()

        cx = SCREEN_WIDTH // 2
        self._btn_easy   = _Button("ЛЕГКО",   cx, 310)
        self._btn_medium = _Button("СРЕДНЕ",  cx, 390)
        self._btn_expert = _Button("ЭКСПЕРТ", cx, 470)
        self._btn_back   = _Button("← НАЗАД",    cx, 570)

        self._font_title = pygame.font.SysFont("monospace", 48, bold=True)
        self._font_desc  = pygame.font.SysFont("monospace", 17)

        # Описания сложностей (отображаются под кнопками)
        self._descriptions = {
            "easy":   "3 пули, длинные паузы между выстрелами",
            "medium": "5 пуль, средние паузы",
            "expert": "8 пуль, короткие паузы, быстрее движение",
        }
        self._hovered: str | None = None

    def run(self) -> str:
        while True:
            self._clock.tick(60)
            self._hovered = self._get_hovered()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "back"
                if self._btn_easy.is_clicked(event):
                    return "easy"
                if self._btn_medium.is_clicked(event):
                    return "medium"
                if self._btn_expert.is_clicked(event):
                    return "expert"
                if self._btn_back.is_clicked(event):
                    return "back"
            self._draw()

    def _get_hovered(self) -> str | None:
        pos = pygame.mouse.get_pos()
        for key, btn in [("easy", self._btn_easy),
                         ("medium", self._btn_medium),
                         ("expert", self._btn_expert)]:
            if btn._rect.collidepoint(pos):
                return key
        return None

    def _draw(self) -> None:
        self._screen.fill(DARK_PURPLE)
        for x, y, b in self._stars:
            self._screen.set_at((x, y), (b, b, b))

        title = self._font_title.render("ВЫБОР СЛОЖНОСТИ", True, YELLOW)
        self._screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=190))

        self._btn_easy.draw(self._screen)
        self._btn_medium.draw(self._screen)
        self._btn_expert.draw(self._screen)
        self._btn_back.draw(self._screen)

        # Подсказка при наведении
        if self._hovered and self._hovered in self._descriptions:
            desc = self._font_desc.render(self._descriptions[self._hovered], True, CYAN)
            self._screen.blit(desc, desc.get_rect(centerx=SCREEN_WIDTH // 2, centery=530))

        pygame.display.flip()


# Ввод имени после поражения

class NameInputScreen:
    """
    Экран ввода имени после Game Over.
    Показывает финальный счёт и просит ввести имя (макс. 16 символов).
    run() возвращает строку с именем (может быть пустой — тогда запись не сохраняется).
    """

    _MAX_LEN = 16

    def __init__(self, screen: pygame.Surface, stars: list, score: int) -> None:
        self._screen = screen
        self._stars  = stars
        self._score  = score
        self._clock  = pygame.time.Clock()
        self._name   = ""

        self._font_title = pygame.font.SysFont("monospace", 44, bold=True)
        self._font_score = pygame.font.SysFont("monospace", 28)
        self._font_label = pygame.font.SysFont("monospace", 22)
        self._font_input = pygame.font.SysFont("monospace", 34, bold=True)
        self._font_hint  = pygame.font.SysFont("monospace", 18)

        # Поле ввода
        self._input_rect = pygame.Rect(0, 0, 380, 52)
        self._input_rect.center = (SCREEN_WIDTH // 2, 430)

        self._cursor_timer = 0.0
        self._cursor_show  = True

    def run(self) -> str:
        while True:
            dt = self._clock.tick(60) / 1000.0
            self._cursor_timer += dt
            if self._cursor_timer >= 0.5:
                self._cursor_timer = 0.0
                self._cursor_show  = not self._cursor_show

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return self._name.strip()
                    elif event.key == pygame.K_ESCAPE:
                        return ""
                    elif event.key == pygame.K_BACKSPACE:
                        self._name = self._name[:-1]
                    elif len(self._name) < self._MAX_LEN:
                        # Добавляем только печатаемые символы
                        if event.unicode.isprintable():
                            self._name += event.unicode

            self._draw()

    def _draw(self) -> None:
        self._screen.fill(DARK_PURPLE)
        for x, y, b in self._stars:
            self._screen.set_at((x, y), (b, b, b))

        cx = SCREEN_WIDTH // 2

        title = self._font_title.render("GAME  OVER", True, RED)
        self._screen.blit(title, title.get_rect(centerx=cx, centery=170))

        score_surf = self._font_score.render(f"Счёт:  {self._score:06d}", True, YELLOW)
        self._screen.blit(score_surf, score_surf.get_rect(centerx=cx, centery=240))

        label = self._font_label.render("Введи своё имя для таблицы рекордов:", True, WHITE)
        self._screen.blit(label, label.get_rect(centerx=cx, centery=340))

        # Поле ввода
        pygame.draw.rect(self._screen, (40, 40, 70),    self._input_rect, border_radius=8)
        pygame.draw.rect(self._screen, CYAN,             self._input_rect, width=2, border_radius=8)

        display_text = self._name + ("|" if self._cursor_show else " ")
        inp_surf = self._font_input.render(display_text, True, WHITE)
        self._screen.blit(inp_surf, inp_surf.get_rect(center=self._input_rect.center))

        hint = self._font_hint.render("Enter — сохранить   Esc — пропустить", True, (150, 150, 180))
        self._screen.blit(hint, hint.get_rect(centerx=cx, centery=500))

        pygame.display.flip()


# Таблица рекордов

class LeaderboardScreen:
    """
    Экран таблицы рекордов. Принимает список записей из Leaderboard.
    run() блокирует до нажатия Esc / Enter / клика по «Назад».
    """

    def __init__(
        self,
        screen: pygame.Surface,
        stars: list,
        records: list[tuple[str, str, int]],   # [(name, difficulty, score), ...]
    ) -> None:
        self._screen  = screen
        self._stars   = stars
        self._records = records
        self._clock   = pygame.time.Clock()

        cx = SCREEN_WIDTH // 2
        self._btn_back = _Button("←  НАЗАД", cx, 630)

        self._font_title  = pygame.font.SysFont("monospace", 44, bold=True)
        self._font_header = pygame.font.SysFont("monospace", 18, bold=True)
        self._font_row    = pygame.font.SysFont("monospace", 20)

        self._diff_colours = {
            "easy":   GREEN,
            "medium": YELLOW,
            "expert": RED,
        }
        self._diff_labels = {
            "easy":   "ЛЕГКО",
            "medium": "СРЕДНЕ",
            "expert": "ЭКСПЕРТ",
        }

    def run(self) -> None:
        while True:
            self._clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if self._btn_back.is_clicked(event):
                    return
            self._draw()

    def _draw(self) -> None:
        self._screen.fill(DARK_PURPLE)
        for x, y, b in self._stars:
            self._screen.set_at((x, y), (b, b, b))

        cx = SCREEN_WIDTH // 2

        title = self._font_title.render("ТАБЛИЦА РЕКОРДОВ", True, YELLOW)
        self._screen.blit(title, title.get_rect(centerx=cx, centery=60))

        # Заголовки колонок
        headers = [("#", 70), ("ИМЯ", 230), ("СЛОЖНОСТЬ", 460), ("СЧЁТ", 640)]
        for text, x in headers:
            h = self._font_header.render(text, True, CYAN)
            self._screen.blit(h, h.get_rect(centerx=x, centery=130))

        # Разделитель
        pygame.draw.line(self._screen, (80, 80, 120), (40, 148), (SCREEN_WIDTH - 40, 148), 1)

        # Строки таблицы (максимум 10)
        for i, (name, diff, score) in enumerate(self._records[:10]):
            y    = 165 + i * 42
            rank_colour = (255, 215, 0) if i == 0 else (200, 200, 200)

            rank = self._font_row.render(f"{i + 1}.", True, rank_colour)
            self._screen.blit(rank, rank.get_rect(centerx=70, centery=y))

            nm = self._font_row.render(name[:16], True, WHITE)
            self._screen.blit(nm, nm.get_rect(centerx=230, centery=y))

            diff_label  = self._diff_labels.get(diff, diff)
            diff_colour = self._diff_colours.get(diff, WHITE)
            dif = self._font_row.render(diff_label, True, diff_colour)
            self._screen.blit(dif, dif.get_rect(centerx=460, centery=y))

            sc = self._font_row.render(f"{score:06d}", True, YELLOW)
            self._screen.blit(sc, sc.get_rect(centerx=640, centery=y))

        if not self._records:
            empty = self._font_row.render("Рекордов пока нет. Сыграй первым!", True, (150, 150, 180))
            self._screen.blit(empty, empty.get_rect(centerx=cx, centery=300))

        self._btn_back.draw(self._screen)
        pygame.display.flip()
