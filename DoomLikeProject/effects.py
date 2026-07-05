"""
effects.py
火球与屏幕特效
"""

import math
import pygame

from settings import *


class Fireball:
    def __init__(self, x, y, dir_x, dir_y, damage):
        self.x = x
        self.y = y

        length = math.hypot(dir_x, dir_y)

        if length <= 0.01:
            self.dir_x = 1.0
            self.dir_y = 0.0
        else:
            self.dir_x = dir_x / length
            self.dir_y = dir_y / length

        self.damage = damage
        self.radius = FIREBALL_RADIUS

        self.active = True

        self.trail = []
        self.max_trail = 12

    def update(self, dt, player):
        if not self.active:
            return None

        self.trail.append((self.x, self.y))

        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        self.x += self.dir_x * FIREBALL_SPEED * dt
        self.y += self.dir_y * FIREBALL_SPEED * dt

        if is_wall(self.x, self.y):
            self.active = False
            return "wall"

        result = self.check_hit(player)

        if result:
            return result

        return None

    def check_hit(self, player):
        dx = self.x - player.x
        dy = self.y - player.y

        distance = math.hypot(dx, dy)

        if distance < self.radius + PLAYER_RADIUS:
            damaged = player.take_damage(self.damage)

            self.active = False

            if damaged:
                return "player"

        return None

    def draw(self, screen, player):
        if not self.active:
            return

        self.draw_trail(screen, player)
        self.draw_core(screen, player)

    def draw_trail(self, screen, player):
        for i, point in enumerate(self.trail):
            trail_x, trail_y = point

            ratio = (i + 1) / max(1, len(self.trail))
            alpha = int(120 * ratio)
            size_mul = 0.45 + 0.55 * ratio

            self.draw_fireball_sprite(
                screen,
                player,
                trail_x,
                trail_y,
                size_mul,
                alpha,
                core=False
            )

    def draw_core(self, screen, player):
        self.draw_fireball_sprite(
            screen,
            player,
            self.x,
            self.y,
            1.0,
            255,
            core=True
        )

    def draw_fireball_sprite(self, screen, player, obj_x, obj_y, size_mul, alpha, core):
        dx = obj_x - player.x
        dy = obj_y - player.y

        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_fireball = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_fireball - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if is_blocked(player.x, player.y, obj_x, obj_y):
            return

        screen_x = (
            SCREEN_WIDTH // 2
            +
            (angle_diff / HALF_FOV)
            *
            (SCREEN_WIDTH // 2)
        )

        size = int(
            FIREBALL_RADIUS
            *
            SCREEN_HEIGHT
            *
            size_mul
            /
            max(distance, 0.4)
        )

        size = max(3, min(size, 90))

        screen_y = SCREEN_HEIGHT // 2 + size // 3

        if core:
            pygame.draw.circle(
                screen,
                (255, 90, 30),
                (int(screen_x), int(screen_y)),
                size + 7
            )

            pygame.draw.circle(
                screen,
                (255, 180, 60),
                (int(screen_x), int(screen_y)),
                size + 2
            )

            pygame.draw.circle(
                screen,
                (255, 245, 170),
                (int(screen_x), int(screen_y)),
                max(2, size // 2)
            )

        else:
            trail_surface = pygame.Surface(
                (size * 4, size * 4),
                pygame.SRCALPHA
            )

            cx = trail_surface.get_width() // 2
            cy = trail_surface.get_height() // 2

            pygame.draw.circle(
                trail_surface,
                (255, 120, 30, alpha),
                (cx, cy),
                size
            )

            pygame.draw.circle(
                trail_surface,
                (255, 220, 90, alpha // 2),
                (cx, cy),
                max(1, size // 2)
            )

            screen.blit(
                trail_surface,
                (
                    int(screen_x - cx),
                    int(screen_y - cy)
                )
            )


class FireballExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.timer = 0.22
        self.duration = 0.22

        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        self.timer -= dt

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

        angle_to_obj = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_obj - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if is_blocked(player.x, player.y, self.x, self.y):
            return

        progress = 1.0 - self.timer / self.duration
        progress = max(0.0, min(1.0, progress))

        alpha = int(220 * (1.0 - progress))

        screen_x = (
            SCREEN_WIDTH // 2
            +
            (angle_diff / HALF_FOV)
            *
            (SCREEN_WIDTH // 2)
        )

        base_size = int(0.45 * SCREEN_HEIGHT / max(distance, 0.5))
        radius = int(base_size * (0.4 + progress * 1.5))
        radius = max(6, min(radius, 160))

        screen_y = SCREEN_HEIGHT // 2 + radius // 3

        surf = pygame.Surface(
            (radius * 4, radius * 4),
            pygame.SRCALPHA
        )

        cx = surf.get_width() // 2
        cy = surf.get_height() // 2

        pygame.draw.circle(
            surf,
            (255, 80, 20, alpha),
            (cx, cy),
            radius,
            max(3, radius // 8)
        )

        pygame.draw.circle(
            surf,
            (255, 210, 80, alpha),
            (cx, cy),
            max(2, radius // 2)
        )

        screen.blit(
            surf,
            (
                int(screen_x - cx),
                int(screen_y - cy)
            )
        )


def draw_damage_flash(screen, player):
    if player.flash_timer <= 0:
        return

    ratio = player.flash_timer / PLAYER_FLASH_DURATION
    ratio = max(0.0, min(1.0, ratio))

    alpha = int(150 * (ratio ** 1.8))

    flash_surface = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    flash_surface.fill((255, 0, 0, alpha))

    screen.blit(flash_surface, (0, 0))


def draw_damage_vignette(screen, player):
    if player.flash_timer <= 0:
        return

    ratio = player.flash_timer / PLAYER_FLASH_DURATION
    ratio = max(0.0, min(1.0, ratio))

    alpha = int(180 * (ratio ** 1.2))

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    thickness = 90

    pygame.draw.rect(
        overlay,
        (120, 0, 0, alpha),
        (0, 0, SCREEN_WIDTH, thickness)
    )

    pygame.draw.rect(
        overlay,
        (120, 0, 0, alpha),
        (0, SCREEN_HEIGHT - thickness, SCREEN_WIDTH, thickness)
    )

    pygame.draw.rect(
        overlay,
        (120, 0, 0, alpha),
        (0, 0, thickness, SCREEN_HEIGHT)
    )

    pygame.draw.rect(
        overlay,
        (120, 0, 0, alpha),
        (SCREEN_WIDTH - thickness, 0, thickness, SCREEN_HEIGHT)
    )

    screen.blit(overlay, (0, 0))


class HealthPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HEALTH_PACK_RADIUS
        self.heal_amount = HEALTH_PACK_HEAL
        self.timer = HEALTH_PACK_LIFETIME
        self.active = True
        self.float_timer = 0.0

    def update(self, dt, player):
        if not self.active:
            return False

        self.timer -= dt
        self.float_timer += dt

        if self.timer <= 0:
            self.active = False
            return False

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= self.radius + PLAYER_RADIUS:
            if player.health < PLAYER_MAX_HEALTH:
                player.health = min(PLAYER_MAX_HEALTH, player.health + self.heal_amount)
                self.active = False
                return True

        return False

    def draw(self, screen, player):
        if not self.active:
            return

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_obj = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_obj - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if is_blocked(player.x, player.y, self.x, self.y):
            return

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        size = int(0.35 * SCREEN_HEIGHT / max(distance, 0.55))
        size = max(12, min(size, 70))
        bob = int(math.sin(self.float_timer * 5.0) * max(2, size * 0.08))
        screen_y = SCREEN_HEIGHT // 2 + size // 2 + bob

        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx = surf.get_width() // 2
        cy = surf.get_height() // 2

        pygame.draw.circle(surf, (30, 130, 50, 190), (cx, cy), size // 2 + 8)
        cross_thickness = max(6, size // 3)
        cross_length = size
        vertical_rect = pygame.Rect(0, 0, cross_thickness, cross_length)
        horizontal_rect = pygame.Rect(0, 0, cross_length, cross_thickness)
        vertical_rect.center = (cx, cy)
        horizontal_rect.center = (cx, cy)

        pygame.draw.rect(surf, (240, 240, 240, 255), vertical_rect, border_radius=3)
        pygame.draw.rect(surf, (240, 240, 240, 255), horizontal_rect, border_radius=3)
        pygame.draw.rect(surf, (40, 180, 70, 255), vertical_rect.inflate(-6, -6), 2, border_radius=3)
        pygame.draw.rect(surf, (40, 180, 70, 255), horizontal_rect.inflate(-6, -6), 2, border_radius=3)

        screen.blit(surf, (int(screen_x - cx), int(screen_y - cy)))


class ArmorPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = ARMOR_PACK_RADIUS
        self.armor_amount = ARMOR_PACK_VALUE
        self.timer = ARMOR_PACK_LIFETIME
        self.active = True
        self.float_timer = 0.0

    def update(self, dt, player):
        if not self.active:
            return False

        self.timer -= dt
        self.float_timer += dt

        if self.timer <= 0:
            self.active = False
            return False

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= self.radius + PLAYER_RADIUS:
            if player.armor < PLAYER_MAX_ARMOR:
                player.armor = min(PLAYER_MAX_ARMOR, player.armor + self.armor_amount)
                self.active = False
                return True

        return False

    def draw(self, screen, player):
        if not self.active:
            return

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_obj = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_obj - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if is_blocked(player.x, player.y, self.x, self.y):
            return

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        size = int(0.35 * SCREEN_HEIGHT / max(distance, 0.55))
        size = max(12, min(size, 70))
        bob = int(math.sin(self.float_timer * 5.0) * max(2, size * 0.08))
        screen_y = SCREEN_HEIGHT // 2 + size // 2 + bob

        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx = surf.get_width() // 2
        cy = surf.get_height() // 2

        shield = [
            (cx, cy - size // 2),
            (cx + size // 2, cy - size // 4),
            (cx + size // 3, cy + size // 3),
            (cx, cy + size // 2),
            (cx - size // 3, cy + size // 3),
            (cx - size // 2, cy - size // 4),
        ]

        pygame.draw.circle(surf, (40, 110, 180, 170), (cx, cy), size // 2 + 8)
        pygame.draw.polygon(surf, (80, 180, 255, 255), shield)
        pygame.draw.polygon(surf, (230, 250, 255, 255), shield, 3)
        pygame.draw.line(surf, (230, 250, 255, 220), (cx, cy - size // 3), (cx, cy + size // 3), 2)

        screen.blit(surf, (int(screen_x - cx), int(screen_y - cy)))


class AmmoPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = AMMO_PACK_RADIUS
        self.ammo_amount = AMMO_PACK_VALUE
        self.timer = AMMO_PACK_LIFETIME
        self.active = True
        self.float_timer = 0.0

    def update(self, dt, game):
        if not self.active:
            return False

        self.timer -= dt
        self.float_timer += dt

        if self.timer <= 0:
            self.active = False
            return False

        dx = self.x - game.player.x
        dy = self.y - game.player.y
        distance = math.hypot(dx, dy)

        if distance <= self.radius + PLAYER_RADIUS:
            if game.shotgun_ammo < SHOTGUN_MAX_AMMO:
                game.shotgun_ammo = min(SHOTGUN_MAX_AMMO, game.shotgun_ammo + self.ammo_amount)
                self.active = False
                return True

        return False

    def draw(self, screen, player):
        if not self.active:
            return

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_obj = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_obj - player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if is_blocked(player.x, player.y, self.x, self.y):
            return

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        size = int(0.34 * SCREEN_HEIGHT / max(distance, 0.55))
        size = max(12, min(size, 68))
        bob = int(math.sin(self.float_timer * 5.0) * max(2, size * 0.08))
        screen_y = SCREEN_HEIGHT // 2 + size // 2 + bob

        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx = surf.get_width() // 2
        cy = surf.get_height() // 2

        pygame.draw.circle(surf, (160, 90, 25, 155), (cx, cy), size // 2 + 8)

        for i in range(3):
            offset = (i - 1) * size // 4
            shell_rect = pygame.Rect(cx - size // 6 + offset, cy - size // 2, size // 4, size)
            pygame.draw.rect(surf, (235, 150, 50), shell_rect, border_radius=4)
            pygame.draw.rect(surf, (255, 220, 120), shell_rect, 2, border_radius=4)
            pygame.draw.rect(surf, (120, 55, 20), (shell_rect.x, shell_rect.bottom - size // 5, shell_rect.width, size // 5))

        screen.blit(surf, (int(screen_x - cx), int(screen_y - cy)))


class BossDeathExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 1.15
        self.duration = 1.15
        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        self.timer -= dt

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

        angle_to_obj = math.atan2(dy, dx)
        angle_diff = normalize_angle(angle_to_obj - player.angle)

        if abs(angle_diff) > HALF_FOV + 0.2:
            return

        progress = 1.0 - self.timer / self.duration
        progress = max(0.0, min(1.0, progress))
        alpha = int(230 * (1.0 - progress))

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        base_size = int(1.3 * SCREEN_HEIGHT / max(distance, 0.65))
        radius = int(base_size * (0.35 + progress * 1.1))
        radius = max(24, min(radius, 300))
        screen_y = SCREEN_HEIGHT // 2 + radius // 5

        surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        cx = surf.get_width() // 2
        cy = surf.get_height() // 2

        for i in range(10):
            a = i * math.pi * 2 / 10 + progress * 4.5
            inner = radius * 0.25
            outer = radius * (0.85 + 0.35 * progress)
            x1 = cx + math.cos(a) * inner
            y1 = cy + math.sin(a) * inner
            x2 = cx + math.cos(a) * outer
            y2 = cy + math.sin(a) * outer
            pygame.draw.line(surf, (255, 180, 70, alpha), (x1, y1), (x2, y2), max(3, radius // 13))

        pygame.draw.circle(surf, (255, 80, 30, alpha), (cx, cy), radius, max(4, radius // 8))
        pygame.draw.circle(surf, (255, 230, 110, alpha), (cx, cy), max(6, radius // 2))
        pygame.draw.circle(surf, (255, 255, 240, alpha), (cx, cy), max(4, radius // 4))

        screen.blit(surf, (int(screen_x - cx), int(screen_y - cy)))
