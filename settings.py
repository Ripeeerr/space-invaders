"""
Настройки и константы игры.
Все числовые параметры хранятся здесь — меняйте этот файл для настройки игры.
"""

#Окно
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 700
FPS   = 60
TITLE = "Space Invaders"

#Цвета
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
YELLOW      = (255, 220,  50)
RED         = (220,  30,  30)
GREEN       = ( 50, 200,  80)
CYAN        = ( 40, 200, 220)
DARK_PURPLE = ( 20,   0,  40)

# Игрок 
PLAYER_SPEED         = 280    # пикселей в секунду
PLAYER_LIVES         = 3
PLAYER_SHOOT_DELAY   = 0.45   # кулдаун между выстрелами (сек)
PLAYER_SCALE         = 0.65   # масштаб спрайта корабля
PLAYER_HITBOX_SHRINK = 0.55   # хитбокс = 55% от видимого размера спрайта
PLAYER_BLINK_TIME    = 1.5    # секунд неуязвимости после попадания
PLAYER_BLINK_RATE    = 0.08   # интервал мигания (сек)

# Враги 
ENEMY_ROWS          = 4
ENEMY_COLS          = 8
ENEMY_H_SPACING     = 76
ENEMY_V_SPACING     = 58
ENEMY_START_Y       = 90
ENEMY_STEP_X        = 16
ENEMY_STEP_Y        = 20
ENEMY_STEP_INTERVAL = 0.85
ENEMY_MIN_INTERVAL  = 0.20
ENEMY_SCALE         = 0.65
ENEMY_ANIM_RATE     = 0.65

# Тип врага для каждого ряда (0 = верхний)
ENEMY_ROW_TYPES = {
    0: "alien1",
    1: "alien2",
    2: "alien3",
    3: "alien4",
}
ENEMY_ROW_SCORES = {
    "alien1": 30,
    "alien2": 20,
    "alien3": 15,
    "alien4": 10,
}

# Стрельба врагов — базовые значения (переопределяются сложностью)
ENEMY_SHOOT_INTERVAL_MIN = 1.8
ENEMY_SHOOT_INTERVAL_MAX = 4.0
ENEMY_MAX_BULLETS        = 3
ENEMY_SHOOT_QUEUE_DELAY  = 0.35

# Волны (бесконечная игра)
WAVE_SPEED_BONUS = 0.08
WAVE_MIN_STEP    = 0.12

# Пули
PLAYER_BULLET_SPEED = 550
ENEMY_BULLET_SPEED  = 220
BULLET_WIDTH  = 4
BULLET_HEIGHT = 16

# Взрывы
EXPLOSION_DURATION = 0.18

# Частицы при попадании
HIT_PARTICLE_COUNT = 8
HIT_PARTICLE_SPEED = 120
HIT_PARTICLE_LIFE  = 0.4

# Пути к ассетам
ASSET_PATHS = {
    "enemies": {
        "alien1": "assets/sprites/alien1.png",
        "alien2": "assets/sprites/alien2.png",
        "alien3": "assets/sprites/alien3.png",
        "alien4": "assets/sprites/alien4.png",
        "alien5": "assets/sprites/alien5.png",
        "alien6": "assets/sprites/alien6.png",
        "alien7": "assets/sprites/alien7.png",
        "alien8": "assets/sprites/alien8.png",
    },
    "player": "assets/sprites/spaceship.png",
    "explosions": [
        "assets/sprites/explosion1.png",
        "assets/sprites/explosion2.png",
        "assets/sprites/explosion3.png",
    ],
    "hearts": {
        "full":  "assets/sprites/heart_full.png",
        "half":  "assets/sprites/heart_half.png",
        "empty": "assets/sprites/heart_empty.png",
    },
}

# Параметры сложности 
# game.py применяет нужный пресет перед созданием Swarm.
DIFFICULTY_PRESETS = {
    "easy": {
        "enemy_shoot_interval_min": 1,   # большие паузы между выстрелами
        "enemy_shoot_interval_max": 2,
        "enemy_max_bullets":        5,     # мало пуль одновременно
        "enemy_shoot_queue_delay":  0.50,
        "wave_speed_bonus":         0.05,  # медленное ускорение с волнами
        "wave_min_step":            0.18,
    },
    "medium": {
        "enemy_shoot_interval_min": 0.6,
        "enemy_shoot_interval_max": 1,
        "enemy_max_bullets":        7,
        "enemy_shoot_queue_delay":  0.35,
        "wave_speed_bonus":         0.08,
        "wave_min_step":            0.12,
    },
    "expert": {
        "enemy_shoot_interval_min": 0.2,   # частые выстрелы
        "enemy_shoot_interval_max": 0.5,
        "enemy_max_bullets":        11,     # много пуль одновременно
        "enemy_shoot_queue_delay":  0.20,
        "wave_speed_bonus":         0.12,  # быстрое ускорение с волнами
        "wave_min_step":            0.08,
    },
}
