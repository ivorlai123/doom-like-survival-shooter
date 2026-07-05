"""
world.py
地图与射线投射渲染
"""

import math
import pygame

from settings import *


class World:
    def __init__(self):
        self.depth_buffer = [MAX_DEPTH] * NUM_RAYS

    # =====================================================
    # 渲染整个世界
    # =====================================================

    def render(self, screen, player):
        self.draw_background(screen, player)
        self.cast_rays(screen, player)

    # =====================================================
    # 天空和地面
    # =====================================================

    def draw_background(self, screen, player):
        sky_color = (30, 30, 40)
        floor_color = (45, 45, 45)
        horizon_color = (70, 70, 78)

        # 天空
        pygame.draw.rect(
            screen,
            sky_color,
            (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        )

        # 地面
        pygame.draw.rect(
            screen,
            floor_color,
            (0, SCREEN_HEIGHT // 2,
             SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        )

        pygame.draw.rect(
            screen,
            horizon_color,
            (0, SCREEN_HEIGHT // 2 - 2, SCREEN_WIDTH, 4)
        )

    # =====================================================
    # 射线投射
    # =====================================================

    def cast_rays(self, screen, player):

        start_angle = player.angle - HALF_FOV
        angle_step = FOV / NUM_RAYS

        current_angle = start_angle

        for ray in range(NUM_RAYS):

            distance, hit_cell = self.cast_single_ray(
                player.x,
                player.y,
                current_angle
            )

            # ------------------------------------------------
            # 鱼眼修正
            # ------------------------------------------------

            corrected_distance = distance * math.cos(
                current_angle - player.angle
            )

            corrected_distance = max(corrected_distance, 0.0001)

            self.depth_buffer[ray] = corrected_distance

            # ------------------------------------------------
            # 墙高
            # ------------------------------------------------

            wall_height = int(SCREEN_HEIGHT / corrected_distance)

            wall_height = min(wall_height, SCREEN_HEIGHT * 2)

            # ------------------------------------------------
            # 距离明暗
            # ------------------------------------------------

            brightness = 1 / (
                1 + corrected_distance * WALL_SHADE_FACTOR
            )

            brightness = max(0.2, min(1.0, brightness))

            base_color = self.get_wall_base_color(hit_cell)

            r = int(base_color[0] * brightness)
            g = int(base_color[1] * brightness)
            b = int(base_color[2] * brightness)

            color = (r, g, b)

            # ------------------------------------------------
            # 墙位置
            # ------------------------------------------------

            wall_top = int(SCREEN_HEIGHT // 2 - wall_height // 2)

            wall_rect = (
                ray * RAY_WIDTH,
                wall_top,
                RAY_WIDTH + 1,
                wall_height
            )

            pygame.draw.rect(screen, color, wall_rect)
            self.draw_wall_detail(screen, ray, wall_top, wall_height, hit_cell, brightness)

            current_angle += angle_step

    def get_wall_base_color(self, hit_cell):
        if hit_cell is None:
            return WALL_BASE_COLOR

        x, y = hit_cell

        if (x, y) in PILLAR_SET:
            return (125, 88, 58)

        if (x + y) % 2 == 0:
            return (112, 112, 108)

        return (92, 96, 100)

    def draw_wall_detail(self, screen, ray, wall_top, wall_height, hit_cell, brightness):
        if hit_cell is None or wall_height <= 18:
            return

        x = ray * RAY_WIDTH
        line_alpha = max(25, min(120, int(95 * brightness)))
        detail = pygame.Surface((RAY_WIDTH + 1, wall_height), pygame.SRCALPHA)

        if ray % 8 == 0:
            pygame.draw.rect(detail, (0, 0, 0, line_alpha), (0, 0, 1, wall_height))
        pygame.draw.rect(detail, (255, 255, 255, line_alpha // 2), (0, wall_height // 3, RAY_WIDTH + 1, 1))
        pygame.draw.rect(detail, (0, 0, 0, line_alpha), (0, wall_height * 2 // 3, RAY_WIDTH + 1, 1))

        screen.blit(detail, (x, wall_top))

    # =====================================================
    # 单根射线
    # =====================================================

    def cast_single_ray(self, start_x, start_y, angle):

        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        distance = 0.0

        step_size = 0.05

        while distance < MAX_DEPTH:

            test_x = start_x + cos_a * distance
            test_y = start_y + sin_a * distance

            if is_wall(test_x, test_y):
                return distance, (int(test_x), int(test_y))

            distance += step_size

        return MAX_DEPTH, None

    # =====================================================
    # 调试小地图（可选）
    # =====================================================

    def draw_debug_minimap(self, screen, player):

        scale = 8

        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):

                rect = pygame.Rect(
                    x * scale,
                    y * scale,
                    scale,
                    scale
                )

                if WORLD_MAP[y][x] == 1:
                    pygame.draw.rect(
                        screen,
                        (120, 120, 120),
                        rect
                    )
                else:
                    pygame.draw.rect(
                        screen,
                        (30, 30, 30),
                        rect
                    )

        # 柱子
        for px, py in PILLAR_POSITIONS:
            pygame.draw.rect(
                screen,
                (180, 120, 40),
                (
                    px * scale,
                    py * scale,
                    scale,
                    scale
                )
            )

        # 玩家
        player_x = int(player.x * scale)
        player_y = int(player.y * scale)

        pygame.draw.circle(
            screen,
            COLOR_GREEN,
            (player_x, player_y),
            4
        )

        # 朝向线
        line_x = player_x + math.cos(player.angle) * 12
        line_y = player_y + math.sin(player.angle) * 12

        pygame.draw.line(
            screen,
            COLOR_GREEN,
            (player_x, player_y),
            (line_x, line_y),
            2
        )
