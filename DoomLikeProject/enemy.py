"""
enemy.py
小恶魔与 Boss 敌人类

素材版：
- 支持 assets/imp.png
- 支持 assets/boss.png
- 没有素材时自动回退到原来的圆形怪物
- 支持屏幕矩形 hitbox，适合贴图后射击判定
"""

import os
import math
import random
import pygame

from settings import *


SPRITE_CACHE = {}


def load_sprite(path):
    if path in SPRITE_CACHE:
        return SPRITE_CACHE[path]

    if not os.path.exists(path):
        SPRITE_CACHE[path] = None
        return None

    try:
        image = pygame.image.load(path).convert_alpha()
        SPRITE_CACHE[path] = image
        return image
    except pygame.error:
        SPRITE_CACHE[path] = None
        return None


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.radius = ENEMY_RADIUS
        self.speed = ENEMY_SPEED

        self.health = ENEMY_HEALTH
        self.damage = ENEMY_DAMAGE
        self.attack_timer = 0.0
        self.dead = False

        self.spawn_visual_timer = 1.0
        self.spawn_visual_duration = 1.0
        self.freeze_timer = 0.0

        self.hit_flash_timer = 0.0
        self.hit_stun_timer = 0.0

        self.stuck_timer = 0.0
        self.strafe_timer = 0.0
        self.strafe_dir = random.choice([-1, 1])

        self.sprite = load_sprite(asset_path("imp.png"))

    def apply_wave_scaling(self, wave):
        """
        Wave Survival 难度成长：波数越高，小恶魔越快、血量越高。
        """
        wave_bonus = max(0, wave - 1)
        self.speed = ENEMY_SPEED * (1.0 + WAVE_ENEMY_SPEED_GROWTH * wave_bonus)
        self.health = int(ENEMY_HEALTH * (1.0 + WAVE_ENEMY_HEALTH_GROWTH * wave_bonus))

    def update(self, dt, player):
        if self.dead:
            return

        old_x = self.x
        old_y = self.y

        if self.spawn_visual_timer > 0:
            self.spawn_visual_timer -= dt

        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            return

        if self.attack_timer > 0:
            self.attack_timer -= dt

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= dt
            return

        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)

        if (
            distance <= ENEMY_ATTACK_RANGE
            and
            not is_blocked(self.x, self.y, player.x, player.y)
        ):
            self.try_attack(player)
        else:
            self.move_towards_player(dt, player, distance)

        moved = math.hypot(self.x - old_x, self.y - old_y)

        if moved < 0.003 and distance > ENEMY_ATTACK_RANGE:
            self.stuck_timer += dt
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 2.0)

        if self.stuck_timer > 0.25:
            self.stuck_timer = 0.0
            self.strafe_timer = 0.45
            self.strafe_dir *= -1

    def move_towards_player(self, dt, player, distance):
        if distance <= 0.01:
            return

        dir_x = (player.x - self.x) / distance
        dir_y = (player.y - self.y) / distance

        side_x = -dir_y
        side_y = dir_x

        if self.strafe_timer > 0:
            self.strafe_timer -= dt

            move_x = dir_x * 0.45 + side_x * self.strafe_dir * 0.90
            move_y = dir_y * 0.45 + side_y * self.strafe_dir * 0.90

            length = math.hypot(move_x, move_y)

            if length > 0.01:
                move_x /= length
                move_y /= length

            self.try_move(
                self.x + move_x * self.speed * dt,
                self.y + move_y * self.speed * dt
            )

            return

        new_x = self.x + dir_x * self.speed * dt
        new_y = self.y + dir_y * self.speed * dt

        before_x = self.x
        before_y = self.y

        self.try_move(new_x, new_y)

        moved = math.hypot(self.x - before_x, self.y - before_y)

        if moved < 0.002:
            for side in (self.strafe_dir, -self.strafe_dir):
                alt_x = self.x + side_x * side * self.speed * dt
                alt_y = self.y + side_y * side * self.speed * dt

                if not self.collides(alt_x, alt_y):
                    self.x = alt_x
                    self.y = alt_y
                    self.strafe_dir = side
                    break

    def try_move(self, new_x, new_y):
        moved = False

        if not self.collides(new_x, self.y):
            self.x = new_x
            moved = True

        if not self.collides(self.x, new_y):
            self.y = new_y
            moved = True

        return moved

    def collides(self, x, y):
        points = [
            (x + self.radius, y),
            (x - self.radius, y),
            (x, y + self.radius),
            (x, y - self.radius),
            (x + self.radius * 0.7, y + self.radius * 0.7),
            (x - self.radius * 0.7, y + self.radius * 0.7),
            (x + self.radius * 0.7, y - self.radius * 0.7),
            (x - self.radius * 0.7, y - self.radius * 0.7),
        ]

        return any(is_wall(px, py) for px, py in points)

    def try_attack(self, player):
        if self.attack_timer > 0:
            return

        player.take_damage(self.damage)
        self.attack_timer = ENEMY_ATTACK_COOLDOWN

    def take_damage(self, damage):
        self.health -= damage

        self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
        self.hit_stun_timer = ENEMY_HIT_STUN_DURATION

        self.strafe_timer = 0.20
        self.strafe_dir *= -1

        if self.health <= 0:
            self.dead = True

    def get_screen_hitbox(self, player):
        return get_sprite_rect(
            player,
            self.x,
            self.y,
            self.radius,
            size_multiplier=2.2,
            width_ratio=0.60,
            height_ratio=0.95,
            is_boss=False
        )

    def draw(self, screen, player):
        if self.dead:
            return

        alpha = 255

        body_color = (180, 40, 30)
        outline_color = (255, 120, 80)

        if self.hit_flash_timer > 0:
            body_color = (255, 245, 220)
            outline_color = (255, 255, 255)

        scale = 2.2

        if self.spawn_visual_timer > 0:
            progress = 1.0 - self.spawn_visual_timer / self.spawn_visual_duration
            progress = max(0.0, min(1.0, progress))
            alpha = int(80 + 175 * progress)
            scale *= 0.45 + 0.55 * progress

        draw_billboard_sprite(
            screen,
            player,
            self.x,
            self.y,
            ENEMY_RADIUS,
            body_color,
            outline_color,
            sprite=self.sprite,
            alpha=alpha,
            size_multiplier=scale,
            is_boss=False,
            hit_flash=self.hit_flash_timer > 0
        )


class FastDemon(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = ENEMY_RADIUS * 0.82
        self.speed = ENEMY_SPEED * 1.75
        self.health = max(1, int(ENEMY_HEALTH * 0.55))
        self.damage = max(1, int(ENEMY_DAMAGE * 0.75))
        self.attack_timer = 0.25
        self.sprite = load_sprite(asset_path("fast_demon.png"))

    def apply_wave_scaling(self, wave):
        wave_bonus = max(0, wave - 1)
        self.speed = ENEMY_SPEED * 1.75 * (1.0 + WAVE_ENEMY_SPEED_GROWTH * wave_bonus)
        self.health = int(ENEMY_HEALTH * 0.55 * (1.0 + WAVE_ENEMY_HEALTH_GROWTH * wave_bonus))

    def get_screen_hitbox(self, player):
        return get_sprite_rect(
            player,
            self.x,
            self.y,
            self.radius,
            size_multiplier=2.0,
            width_ratio=0.62,
            height_ratio=0.90,
            is_boss=False
        )

    def draw(self, screen, player):
        if self.dead:
            return

        alpha = 255
        body_color = (230, 85, 25)
        outline_color = (255, 190, 80)

        if self.hit_flash_timer > 0:
            body_color = (255, 245, 220)
            outline_color = (255, 255, 255)

        scale = 2.0

        if self.spawn_visual_timer > 0:
            progress = 1.0 - self.spawn_visual_timer / self.spawn_visual_duration
            progress = max(0.0, min(1.0, progress))
            alpha = int(80 + 175 * progress)
            scale *= 0.45 + 0.55 * progress

        draw_billboard_sprite(
            screen,
            player,
            self.x,
            self.y,
            self.radius,
            body_color,
            outline_color,
            sprite=self.sprite,
            alpha=alpha,
            size_multiplier=scale,
            is_boss=False,
            hit_flash=self.hit_flash_timer > 0
        )


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.radius = BOSS_RADIUS
        self.speed = BOSS_SPEED

        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.damage = BOSS_DAMAGE

        self.attack_timer = 1.4
        self.charge_timer = 0.0

        self.state = "IDLE"
        self.dead = False

        self.hit_flash_timer = 0.0
        self.hit_stun_timer = 0.0

        self.spawn_visual_timer = 1.4
        self.spawn_visual_duration = 1.4
        self.freeze_timer = 0.0

        self.float_timer = 0.0

        self.orbit_dir = random.choice([-1, 1])
        self.orbit_timer = 1.8

        self.sprite = load_sprite(asset_path("boss.png"))

    def apply_wave_scaling(self, wave):
        """
        Wave Survival 难度成长：波数越高，Boss 越硬、移动略快。
        """
        wave_bonus = max(0, wave - 1)
        self.speed = BOSS_SPEED * (1.0 + WAVE_BOSS_SPEED_GROWTH * wave_bonus)
        self.max_health = int(BOSS_HEALTH * (1.0 + WAVE_BOSS_HEALTH_GROWTH * wave_bonus))
        self.health = self.max_health

    def update(self, dt, player, fireballs, play_sound=None):
        if self.dead:
            return

        self.float_timer += dt

        if self.spawn_visual_timer > 0:
            self.spawn_visual_timer -= dt

        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= dt
            return

        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.orbit_timer -= dt

        if self.orbit_timer <= 0:
            self.orbit_timer = random.uniform(1.2, 2.4)
            self.orbit_dir *= -1

        if self.state == "CHARGING":
            self.charge_timer -= dt

            if self.charge_timer <= 0:
                self.shoot_fireball(player, fireballs, play_sound)
                self.state = "IDLE"
                self.attack_timer = self.get_attack_cooldown()

            return

        self.move_towards_player(dt, player)

        if self.attack_timer <= 0:
            self.state = "CHARGING"
            self.charge_timer = self.get_charge_duration()

    def get_health_ratio(self):
        return max(0.0, self.health / self.max_health)

    def get_attack_cooldown(self):
        ratio = self.get_health_ratio()

        if ratio < 0.25:
            return BOSS_ATTACK_COOLDOWN * 0.55

        if ratio < 0.55:
            return BOSS_ATTACK_COOLDOWN * 0.75

        return BOSS_ATTACK_COOLDOWN

    def get_charge_duration(self):
        ratio = self.get_health_ratio()

        if ratio < 0.25:
            return BOSS_CHARGE_DURATION * 0.60

        if ratio < 0.55:
            return BOSS_CHARGE_DURATION * 0.80

        return BOSS_CHARGE_DURATION

    def move_towards_player(self, dt, player):
        dx = player.x - self.x
        dy = player.y - self.y

        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        dir_x = dx / distance
        dir_y = dy / distance

        side_x = -dir_y
        side_y = dir_x

        speed = self.speed

        if self.get_health_ratio() < 0.5:
            speed *= 1.25

        if distance > 3.6:
            forward_weight = 0.42
        elif distance < 2.8:
            forward_weight = -0.35
        else:
            forward_weight = -0.05

        side_weight = 1.15 * self.orbit_dir

        if self.state == "CHARGING":
            side_weight *= 0.35

        move_x = dir_x * forward_weight + side_x * side_weight
        move_y = dir_y * forward_weight + side_y * side_weight

        length = math.hypot(move_x, move_y)

        if length <= 0.01:
            return

        move_x /= length
        move_y /= length

        moved = self.try_move(
            self.x + move_x * speed * dt,
            self.y + move_y * speed * dt
        )

        if not moved:
            self.orbit_dir *= -1

    def try_move(self, new_x, new_y):
        moved = False

        if not self.collides(new_x, self.y):
            self.x = new_x
            moved = True

        if not self.collides(self.x, new_y):
            self.y = new_y
            moved = True

        return moved

    def collides(self, x, y):
        points = [
            (x + self.radius, y),
            (x - self.radius, y),
            (x, y + self.radius),
            (x, y - self.radius),
            (x + self.radius * 0.7, y + self.radius * 0.7),
            (x - self.radius * 0.7, y + self.radius * 0.7),
            (x + self.radius * 0.7, y - self.radius * 0.7),
            (x - self.radius * 0.7, y - self.radius * 0.7),
        ]

        return any(is_wall(px, py) for px, py in points)

    def shoot_fireball(self, player, fireballs, play_sound=None):
        dx = player.x - self.x
        dy = player.y - self.y

        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        dir_x = dx / distance
        dir_y = dy / distance

        from effects import Fireball

        spawn_x = self.x + dir_x * self.radius * 1.4
        spawn_y = self.y + dir_y * self.radius * 1.4

        fireballs.append(
            Fireball(
                spawn_x,
                spawn_y,
                dir_x,
                dir_y,
                self.damage
            )
        )

        if self.get_health_ratio() < 0.55:
            side_x = -dir_y
            side_y = dir_x

            fireballs.append(
                Fireball(
                    spawn_x + side_x * 0.18,
                    spawn_y + side_y * 0.18,
                    dir_x * 0.98 + side_x * 0.18,
                    dir_y * 0.98 + side_y * 0.18,
                    self.damage
                )
            )

            fireballs.append(
                Fireball(
                    spawn_x - side_x * 0.18,
                    spawn_y - side_y * 0.18,
                    dir_x * 0.98 - side_x * 0.18,
                    dir_y * 0.98 - side_y * 0.18,
                    self.damage
                )
            )

        if play_sound:
            play_sound("fireball")

    def take_damage(self, damage):
        self.health -= damage

        self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
        self.hit_stun_timer = ENEMY_HIT_STUN_DURATION

        self.orbit_dir *= -1

        if self.health <= 0:
            self.health = 0
            self.dead = True

    def get_screen_hitbox(self, player):
        return get_sprite_rect(
            player,
            self.x,
            self.y,
            self.radius,
            size_multiplier=1.75,
            width_ratio=0.78,
            height_ratio=0.82,
            is_boss=True
        )

    def draw(self, screen, player):
        if self.dead:
            return

        alpha = 255
        scale = 1.75

        if self.spawn_visual_timer > 0:
            progress = 1.0 - self.spawn_visual_timer / self.spawn_visual_duration
            progress = max(0.0, min(1.0, progress))
            alpha = int(70 + 185 * progress)
            scale = 0.8 + 0.95 * progress

        pulse = 1.0 + math.sin(self.float_timer * 5.0) * 0.055
        scale *= pulse

        if self.hit_flash_timer > 0:
            color = (255, 245, 220)
            outline = (255, 255, 255)
        elif self.state == "CHARGING":
            color = (255, 45, 45)
            outline = (255, 190, 120)
        elif self.get_health_ratio() < 0.25:
            color = (190, 20, 40)
            outline = (255, 120, 80)
        elif self.get_health_ratio() < 0.55:
            color = (160, 30, 120)
            outline = (255, 120, 230)
        else:
            color = (120, 20, 160)
            outline = (230, 160, 255)

        draw_billboard_sprite(
            screen,
            player,
            self.x,
            self.y,
            BOSS_RADIUS,
            color,
            outline,
            sprite=self.sprite,
            size_multiplier=scale,
            alpha=alpha,
            is_boss=True,
            charging=(self.state == "CHARGING"),
            charge_ratio=self.get_charge_draw_ratio(),
            hit_flash=self.hit_flash_timer > 0
        )

    def get_charge_draw_ratio(self):
        duration = self.get_charge_duration()

        if duration <= 0:
            return 0.0

        if self.state != "CHARGING":
            return 0.0

        return 1.0 - max(
            0.0,
            min(1.0, self.charge_timer / duration)
        )


def get_sprite_rect(
    player,
    obj_x,
    obj_y,
    radius,
    size_multiplier=1.0,
    width_ratio=0.75,
    height_ratio=0.90,
    is_boss=False
):
    dx = obj_x - player.x
    dy = obj_y - player.y

    distance = math.hypot(dx, dy)

    if distance <= 0.01:
        return None

    angle_to_obj = math.atan2(dy, dx)
    angle_diff = normalize_angle(angle_to_obj - player.angle)

    fov_margin = 0.16 if is_boss else 0.0

    if abs(angle_diff) > HALF_FOV + fov_margin:
        return None

    if is_boss:
        if is_large_sprite_fully_blocked(player, obj_x, obj_y, radius):
            return None
    else:
        if is_blocked(player.x, player.y, obj_x, obj_y):
            return None

    screen_x = (
        SCREEN_WIDTH // 2
        +
        (angle_diff / HALF_FOV)
        *
        (SCREEN_WIDTH // 2)
    )

    size = int(
        radius
        *
        SCREEN_HEIGHT
        *
        size_multiplier
        /
        max(distance, 0.5)
    )

    size = max(8, min(size, 320))

    screen_y = SCREEN_HEIGHT // 2 + size // 3

    rect_w = int(size * 2 * width_ratio)
    rect_h = int(size * 2 * height_ratio)

    return pygame.Rect(
        int(screen_x - rect_w // 2),
        int(screen_y - rect_h // 2),
        rect_w,
        rect_h
    )


def draw_billboard_sprite(
    screen,
    player,
    obj_x,
    obj_y,
    radius,
    color,
    outline,
    sprite=None,
    size_multiplier=1.0,
    alpha=255,
    is_boss=False,
    charging=False,
    charge_ratio=0.0,
    hit_flash=False
):
    rect = get_sprite_rect(
        player,
        obj_x,
        obj_y,
        radius,
        size_multiplier=size_multiplier,
        width_ratio=0.78 if is_boss else 0.60,
        height_ratio=0.82 if is_boss else 0.95,
        is_boss=is_boss
    )

    if rect is None:
        return

    size = max(rect.width, rect.height) // 2

    if is_boss:
        float_offset = int(
            math.sin(pygame.time.get_ticks() * 0.004)
            *
            max(4, size * 0.035)
        )
        rect.y += float_offset

    if charging:
        center = rect.center
        ring_radius = int(max(rect.width, rect.height) * 0.65 + 18 * charge_ratio)
        ring_alpha = int(80 + 150 * charge_ratio)

        ring_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            ring_surface,
            (255, 80, 40, ring_alpha),
            center,
            ring_radius,
            4
        )

        screen.blit(ring_surface, (0, 0))

    if sprite is not None:
        image = pygame.transform.smoothscale(
            sprite,
            (rect.width, rect.height)
        )

        if alpha < 255 or hit_flash:
            image = image.copy()

            if alpha < 255:
                image.set_alpha(alpha)

            if hit_flash:
                flash = pygame.Surface(
                    image.get_size(),
                    pygame.SRCALPHA
                )
                flash.fill((255, 255, 255, 120))
                image.blit(
                    flash,
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_ADD
                )

        screen.blit(image, rect.topleft)
        return

    surf_size = (size + 26) * 2

    surf = pygame.Surface(
        (surf_size, surf_size),
        pygame.SRCALPHA
    )

    cx = surf_size // 2
    cy = surf_size // 2

    pygame.draw.circle(
        surf,
        (*outline, alpha),
        (cx, cy),
        size + 4
    )

    pygame.draw.circle(
        surf,
        (*color, alpha),
        (cx, cy),
        size
    )

    eye_radius = max(2, size // 4)

    pygame.draw.circle(
        surf,
        (*COLOR_WHITE, alpha),
        (cx, int(cy - size * 0.20)),
        eye_radius,
    )

    pygame.draw.circle(
        surf,
        (*COLOR_BLACK, alpha),
        (cx, int(cy - size * 0.20)),
        max(1, eye_radius // 2),
    )

    if is_boss:
        pygame.draw.circle(
            surf,
            (255, 40, 40, alpha),
            (cx, int(cy - size * 0.20)),
            max(1, eye_radius // 4),
        )

    screen.blit(
        surf,
        (
            rect.centerx - cx,
            rect.centery - cy
        )
    )


def is_large_sprite_fully_blocked(player, obj_x, obj_y, radius):
    dx = obj_x - player.x
    dy = obj_y - player.y

    distance = math.hypot(dx, dy)

    if distance <= 0.01:
        return False

    dir_x = dx / distance
    dir_y = dy / distance

    side_x = -dir_y
    side_y = dir_x

    sample_points = [
        (obj_x, obj_y),
        (obj_x + side_x * radius * 0.35, obj_y + side_y * radius * 0.35),
        (obj_x - side_x * radius * 0.35, obj_y - side_y * radius * 0.35),
        (obj_x + side_x * radius * 0.8, obj_y + side_y * radius * 0.8),
        (obj_x - side_x * radius * 0.8, obj_y - side_y * radius * 0.8),
        (obj_x + side_x * radius * 1.4, obj_y + side_y * radius * 1.4),
        (obj_x - side_x * radius * 1.4, obj_y - side_y * radius * 1.4),
    ]

    for sx, sy in sample_points:
        if not is_blocked(player.x, player.y, sx, sy):
            return False

    return True
