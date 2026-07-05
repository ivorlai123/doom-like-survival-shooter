"""
player.py
玩家类
"""

import math
import random
import pygame

from settings import *


class Player:
    def __init__(self):
        self.x = PLAYER_START_X
        self.y = PLAYER_START_Y
        self.angle = PLAYER_START_ANGLE

        self.health = PLAYER_MAX_HEALTH
        self.armor = 0

        self.shoot_timer = 0.0
        self.invincible_timer = 0.0
        self.flash_timer = 0.0

        # 受伤瞬间轻微视角冲击
        self.hurt_kick_timer = 0.0
        self.hurt_kick_dir = 1

    def update(self, dt, keys):
        self.update_timers(dt)
        self.handle_rotation(dt, keys)
        self.handle_movement(dt, keys)
        self.update_hurt_kick(dt)

    def update_timers(self, dt):
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.hurt_kick_timer > 0:
            self.hurt_kick_timer -= dt

    def handle_rotation(self, dt, keys):
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.angle -= PLAYER_ROT_SPEED * dt

        if keys[pygame.K_e] or keys[pygame.K_RIGHT]:
            self.angle += PLAYER_ROT_SPEED * dt

        self.angle = self.normalize_angle(self.angle)

    def update_hurt_kick(self, dt):
        """
        受伤时轻微视角偏移。
        不做 pitch，只做横向角度小冲击，保持老 Doom 风格。
        """

        if self.hurt_kick_timer <= 0:
            return

        ratio = self.hurt_kick_timer / PLAYER_HURT_KICK_DURATION
        kick = PLAYER_HURT_KICK_POWER * ratio * self.hurt_kick_dir

        self.angle += kick * dt * 60
        self.angle = self.normalize_angle(self.angle)

    def handle_movement(self, dt, keys):
        move_x = 0.0
        move_y = 0.0

        forward_x = math.cos(self.angle)
        forward_y = math.sin(self.angle)

        right_x = math.cos(self.angle + math.pi / 2)
        right_y = math.sin(self.angle + math.pi / 2)

        if keys[pygame.K_w]:
            move_x += forward_x
            move_y += forward_y

        if keys[pygame.K_s]:
            move_x -= forward_x
            move_y -= forward_y

        if keys[pygame.K_d]:
            move_x += right_x
            move_y += right_y

        if keys[pygame.K_a]:
            move_x -= right_x
            move_y -= right_y

        length = math.hypot(move_x, move_y)

        if length > 0:
            move_x /= length
            move_y /= length

        new_x = self.x + move_x * PLAYER_SPEED * dt
        new_y = self.y + move_y * PLAYER_SPEED * dt

        self.try_move(new_x, new_y)

    def try_move(self, new_x, new_y):
        if not self.collides(new_x, self.y):
            self.x = new_x

        if not self.collides(self.x, new_y):
            self.y = new_y

    def collides(self, x, y):
        check_points = [
            (x + PLAYER_RADIUS, y),
            (x - PLAYER_RADIUS, y),
            (x, y + PLAYER_RADIUS),
            (x, y - PLAYER_RADIUS),
        ]

        for px, py in check_points:
            if is_wall(px, py):
                return True

        return False

    def can_shoot(self):
        return self.shoot_timer <= 0

    def reset_shoot_timer(self, cooldown=SHOOT_COOLDOWN):
        self.shoot_timer = cooldown

    def take_damage(self, damage):
        if self.invincible_timer > 0:
            return False

        if self.armor > 0:
            armor_absorb = min(self.armor, int(math.ceil(damage * PLAYER_ARMOR_ABSORB_RATIO)))
            self.armor -= armor_absorb
            damage -= armor_absorb

        self.health -= damage
        self.health = max(0, self.health)

        self.invincible_timer = PLAYER_INVINCIBLE_DURATION
        self.flash_timer = PLAYER_FLASH_DURATION

        self.hurt_kick_timer = PLAYER_HURT_KICK_DURATION
        self.hurt_kick_dir = random.choice([-1, 1])

        return True

    def is_dead(self):
        return self.health <= 0

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        return angle
