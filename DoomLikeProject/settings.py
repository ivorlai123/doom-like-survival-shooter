"""
settings.py
游戏全局常量与地图配置
"""

import math
import os
import random

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(filename):
    return os.path.join(PROJECT_DIR, "assets", filename)


def sound_path(filename):
    return os.path.join(PROJECT_DIR, "sounds", filename)


def data_path(filename):
    return os.path.join(PROJECT_DIR, filename)

# =========================================================
# 窗口设置
# =========================================================

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 120

# =========================================================
# 射线投射设置
# =========================================================

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 320
RAY_WIDTH = SCREEN_WIDTH // NUM_RAYS
MAX_DEPTH = 30

WALL_SHADE_FACTOR = 0.15

# =========================================================
# 玩家设置
# =========================================================

PLAYER_START_X = 5.5
PLAYER_START_Y = 5.5
PLAYER_START_ANGLE = 0

PLAYER_SPEED = 5.0
PLAYER_ROT_SPEED = 4.0

PLAYER_RADIUS = 0.2
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ARMOR = 100
PLAYER_ARMOR_ABSORB_RATIO = 0.60

PLAYER_INVINCIBLE_DURATION = 0.5

# 受伤反馈：比之前长，玩家能明显感受到
PLAYER_FLASH_DURATION = 0.28
PLAYER_HURT_KICK_DURATION = 0.18
PLAYER_HURT_KICK_POWER = 0.035

# =========================================================
# 武器设置
# =========================================================

SHOOT_DAMAGE = 34
SHOOT_COOLDOWN = 0.1

HIT_ANGLE_THRESHOLD = 0.08

# 命中反馈
ENEMY_HIT_FLASH_DURATION = 0.08
ENEMY_HIT_STUN_DURATION = 0.10

# =========================================================
# 小恶魔设置
# =========================================================

ENEMY_COUNT = 8

ENEMY_SPEED = 0.75
ENEMY_RADIUS = 0.22

ENEMY_HEALTH = SHOOT_DAMAGE * 3

ENEMY_DAMAGE = 5

ENEMY_ATTACK_RANGE = 0.65
ENEMY_ATTACK_COOLDOWN = 1.5

# =========================================================
# BOSS 设置
# =========================================================

BOSS_HEALTH = SHOOT_DAMAGE * 15

BOSS_SPEED = PLAYER_SPEED * 0.45
BOSS_RADIUS = 0.72

BOSS_DAMAGE = 20

BOSS_ATTACK_COOLDOWN = 2.0
BOSS_CHARGE_DURATION = 0.8

# =========================================================
# 火球设置
# =========================================================

FIREBALL_SPEED = 4.5
FIREBALL_RADIUS = 0.12

# =========================================================
# 传送门设置
# =========================================================

PORTAL_SMALL_RADIUS = 30
PORTAL_SMALL_DURATION = 0.5

PORTAL_BIG_RADIUS = 60
PORTAL_BIG_DURATION = 1.2

# =========================================================
# 颜色
# =========================================================

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

COLOR_RED = (255, 0, 0)
COLOR_DARK_RED = (120, 0, 0)

COLOR_YELLOW = (255, 220, 40)

COLOR_GREEN = (0, 255, 0)

COLOR_PURPLE = (140, 0, 180)

COLOR_GRAY = (110, 110, 110)
COLOR_DARK_GRAY = (60, 60, 60)

WALL_BASE_COLOR = (120, 120, 120)

# =========================================================
# 地图
# =========================================================

MAP_SIZE = 30

WORLD_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1],

    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1],

    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# =========================================================
# 柱子
# =========================================================

PILLAR_POSITIONS = [
    (11, 11),
    (11, 18),
    (18, 11),
    (18, 18),

    (14, 11),
    (15, 18),
]

PILLAR_SET = set(PILLAR_POSITIONS)

# =========================================================
# 中心区域
# =========================================================

CENTER_X_START = 9
CENTER_X_END = 20

CENTER_Y_START = 9
CENTER_Y_END = 20

# =========================================================
# 传送门位置
# =========================================================

ENEMY_PORTAL_POSITIONS = [
    (2.5, 3.5),
    (10.5, 3.5),
    (20.5, 3.5),
    (26.5, 3.5),

    (3.5, 24.5),
    (10.5, 26.5),
    (20.5, 26.5),
    (26.5, 24.5),
]

BOSS_PORTAL_POSITION = (14.5, 15.5)


def clone_map(source_map):
    return [row[:] for row in source_map]


def make_empty_arena_map():
    arena_map = []

    for y in range(MAP_SIZE):
        row = []

        for x in range(MAP_SIZE):
            if x == 0 or y == 0 or x == MAP_SIZE - 1 or y == MAP_SIZE - 1:
                row.append(1)
            else:
                row.append(0)

        arena_map.append(row)

    return arena_map


def add_wall_line(target_map, x1, y1, x2, y2):
    if x1 == x2:
        start_y = min(y1, y2)
        end_y = max(y1, y2)

        for y in range(start_y, end_y + 1):
            target_map[y][x1] = 1

        return

    if y1 == y2:
        start_x = min(x1, x2)
        end_x = max(x1, x2)

        for x in range(start_x, end_x + 1):
            target_map[y1][x] = 1


def make_doom_keep_map():
    arena_map = make_empty_arena_map()

    wall_lines = [
        (6, 4, 6, 11),
        (23, 4, 23, 11),
        (6, 18, 6, 25),
        (23, 18, 23, 25),
        (9, 7, 13, 7),
        (16, 7, 20, 7),
        (9, 22, 13, 22),
        (16, 22, 20, 22),
        (12, 12, 12, 17),
        (17, 12, 17, 17),
    ]

    for line in wall_lines:
        add_wall_line(arena_map, *line)

    return arena_map


def make_techbase_map():
    arena_map = make_empty_arena_map()

    wall_lines = [
        (4, 6, 11, 6),
        (18, 6, 25, 6),
        (4, 23, 11, 23),
        (18, 23, 25, 23),
        (14, 3, 14, 9),
        (15, 20, 15, 26),
        (8, 12, 8, 17),
        (21, 12, 21, 17),
        (11, 14, 13, 14),
        (16, 15, 18, 15),
    ]

    for line in wall_lines:
        add_wall_line(arena_map, *line)

    return arena_map


def make_broken_ring_map():
    arena_map = make_empty_arena_map()

    wall_lines = [
        (7, 7, 11, 7),
        (18, 7, 22, 7),
        (7, 22, 11, 22),
        (18, 22, 22, 22),
        (7, 7, 7, 11),
        (22, 7, 22, 11),
        (7, 18, 7, 22),
        (22, 18, 22, 22),
        (12, 10, 17, 10),
        (12, 19, 17, 19),
        (10, 12, 10, 17),
        (19, 12, 19, 17),
    ]

    for line in wall_lines:
        add_wall_line(arena_map, *line)

    return arena_map


MAP_PRESETS = [
    {
        "name": "Doom Keep",
        "world_map": make_doom_keep_map(),
        "pillars": [
            (10, 10),
            (19, 10),
            (10, 19),
            (19, 19),
        ],
    },
    {
        "name": "Techbase Split",
        "world_map": make_techbase_map(),
        "pillars": [
            (11, 11),
            (18, 11),
            (11, 18),
            (18, 18),
        ],
    },
    {
        "name": "Broken Ring",
        "world_map": make_broken_ring_map(),
        "pillars": [
            (13, 13),
            (16, 13),
            (13, 16),
            (16, 16),
        ],
    },
]


def apply_map_preset(index):
    preset = MAP_PRESETS[index % len(MAP_PRESETS)]

    WORLD_MAP[:] = clone_map(preset["world_map"])
    PILLAR_POSITIONS[:] = list(preset["pillars"])
    PILLAR_SET.clear()
    PILLAR_SET.update(PILLAR_POSITIONS)

    return preset["name"]


def choose_random_map_preset():
    return apply_map_preset(random.randrange(len(MAP_PRESETS)))

# =========================================================
# 工具函数
# =========================================================

def is_wall(x, y):
    """
    判断坐标是否为墙或柱子
    """

    ix = int(x)
    iy = int(y)

    if ix < 0 or ix >= MAP_SIZE:
        return True

    if iy < 0 or iy >= MAP_SIZE:
        return True

    if WORLD_MAP[iy][ix] == 1:
        return True

    if (ix, iy) in PILLAR_SET:
        return True

    return False


def is_blocked(x1, y1, x2, y2):
    """
    Return True if a wall or pillar blocks the straight line between two points.
    """

    distance = math.hypot(x2 - x1, y2 - y1)

    if distance <= 0.01:
        return False

    angle = math.atan2(y2 - y1, x2 - x1)
    step = 0.05
    current = step

    while current < distance:
        test_x = x1 + math.cos(angle) * current
        test_y = y1 + math.sin(angle) * current

        if is_wall(test_x, test_y):
            return True

        current += step

    return False


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2 * math.pi

    while angle < -math.pi:
        angle += 2 * math.pi

    return angle


def is_in_center_area(x, y):
    """
    判断是否位于中心战场
    """

    return (
        CENTER_X_START <= x <= CENTER_X_END
        and
        CENTER_Y_START <= y <= CENTER_Y_END
    )
# =========================================================
# 新增：双武器、回血包、Wave 难度成长
# =========================================================

WEAPON_PISTOL = "PISTOL"
WEAPON_SHOTGUN = "SHOTGUN"

PISTOL_DAMAGE = SHOOT_DAMAGE
PISTOL_COOLDOWN = SHOOT_COOLDOWN
PISTOL_KNOCKBACK = 0.040

SHOTGUN_PELLETS = 7
SHOTGUN_PELLET_DAMAGE = 16
SHOTGUN_COOLDOWN = 0.65
SHOTGUN_SPREAD = 0.11
SHOTGUN_KNOCKBACK = 0.075
SHOTGUN_START_AMMO = 12
SHOTGUN_MAX_AMMO = 36

HEALTH_PACK_DROP_CHANCE = 0.22
HEALTH_PACK_HEAL = 20
HEALTH_PACK_RADIUS = 0.24
HEALTH_PACK_LIFETIME = 18.0

ARMOR_PACK_DROP_CHANCE = 0.14
ARMOR_PACK_VALUE = 25
ARMOR_PACK_RADIUS = 0.24
ARMOR_PACK_LIFETIME = 18.0

AMMO_PACK_DROP_CHANCE = 0.18
AMMO_PACK_VALUE = 6
AMMO_PACK_RADIUS = 0.24
AMMO_PACK_LIFETIME = 18.0

WAVE_ENEMY_SPEED_GROWTH = 0.08
WAVE_ENEMY_HEALTH_GROWTH = 0.12
WAVE_BOSS_HEALTH_GROWTH = 0.18
WAVE_BOSS_SPEED_GROWTH = 0.06
WAVE_SCORE_GROWTH = 0.10
