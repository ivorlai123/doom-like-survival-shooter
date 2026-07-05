"""
portal.py
传送门系统：支持 assets/portal.png 素材；素材不存在时回退为 pygame 绘制椭圆传送门。
"""

import os
import math
import pygame
from settings import *


PORTAL_SPRITE = None
PORTAL_SPRITE_LOADED = False


def load_portal_sprite():
    global PORTAL_SPRITE, PORTAL_SPRITE_LOADED

    if PORTAL_SPRITE_LOADED:
        return PORTAL_SPRITE

    PORTAL_SPRITE_LOADED = True
    path = asset_path("portal.png")

    if not os.path.exists(path):
        PORTAL_SPRITE = None
        return None

    try:
        PORTAL_SPRITE = pygame.image.load(path).convert_alpha()
    except pygame.error:
        PORTAL_SPRITE = None

    return PORTAL_SPRITE


class Portal:
    def __init__(self, x, y, radius, duration, spawn_callback, spawn_time=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.timer = duration
        self.elapsed = 0.0

        self.spawn_callback = spawn_callback
        self.spawn_time = spawn_time if spawn_time is not None else duration

        self.spawned = False
        self.finished = False
        self.sprite = load_portal_sprite()

    def update(self, dt):
        if self.finished:
            return

        self.elapsed += dt
        self.timer -= dt

        if not self.spawned and self.elapsed >= self.spawn_time:
            self.spawn_callback(self.x, self.y)
            self.spawned = True

        if self.timer <= 0:
            self.finished = True

    def draw(self, screen, player):
        if self.finished:
            return

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_portal = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_portal - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if self.is_occluded(player, distance, angle_to_portal):
            return

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        size = int(self.radius * 2.6 / max(distance, 0.7))
        size = max(18, min(size, 260))

        if self.sprite is not None:
            self.draw_sprite(screen, screen_x, size)
        else:
            self.draw_fallback_portal(screen, screen_x, size)

    def draw_sprite(self, screen, screen_x, size):
        width = size * 2
        height = size * 3
        screen_y = SCREEN_HEIGHT // 2 + size // 2

        image = pygame.transform.smoothscale(self.sprite, (width, height))
        pulse_alpha = int(210 + 45 * math.sin(pygame.time.get_ticks() * 0.01))
        image = image.copy()
        image.set_alpha(max(120, min(255, pulse_alpha)))

        glow = pygame.Surface((width + size, height + size), pygame.SRCALPHA)
        gx = glow.get_width() // 2
        gy = glow.get_height() // 2
        pygame.draw.ellipse(
            glow,
            (170, 0, 255, 65),
            (size // 2, size // 2, width, height)
        )

        screen.blit(glow, (int(screen_x - gx), int(screen_y - gy)))
        screen.blit(image, (int(screen_x - width // 2), int(screen_y - height // 2)))

    def draw_fallback_portal(self, screen, screen_x, size):
        width = size * 2
        height = size * 3
        screen_y = SCREEN_HEIGHT // 2 + size // 2

        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        alpha = int(175 + 70 * math.sin(pygame.time.get_ticks() * 0.012))
        alpha = max(90, min(255, alpha))

        pygame.draw.ellipse(
            surf,
            (90, 0, 150, alpha // 2),
            (int(width * 0.18), int(height * 0.10), int(width * 0.64), int(height * 0.80)),
        )

        pygame.draw.ellipse(
            surf,
            (190, 0, 255, alpha),
            (0, 0, width, height),
            max(4, size // 7),
        )

        pygame.draw.ellipse(
            surf,
            (230, 120, 255, alpha),
            (int(width * 0.08), int(height * 0.05), int(width * 0.84), int(height * 0.90)),
            max(2, size // 12),
        )

        cx = width // 2
        cy = height // 2
        rotation = pygame.time.get_ticks() * 0.004

        for i in range(7):
            a = rotation + i * math.pi * 2 / 7

            x1 = cx + math.cos(a) * size * 0.20
            y1 = cy + math.sin(a) * size * 0.50

            x2 = cx + math.cos(a) * size * 0.72
            y2 = cy + math.sin(a) * size * 1.15

            pygame.draw.line(
                surf,
                (255, 170, 255, alpha),
                (x1, y1),
                (x2, y2),
                max(2, size // 11),
            )

        pygame.draw.ellipse(
            surf,
            (255, 210, 255, alpha),
            (int(width * 0.35), int(height * 0.37), int(width * 0.30), int(height * 0.26)),
        )

        screen.blit(surf, (int(screen_x - width // 2), int(screen_y - height // 2)))

    def is_occluded(self, player, target_distance, angle):
        current = 0.05
        step = 0.05

        while current < target_distance:
            test_x = player.x + math.cos(angle) * current
            test_y = player.y + math.sin(angle) * current

            if is_wall(test_x, test_y):
                return True

            current += step

        return False
