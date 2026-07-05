"""
ui.py
游戏 UI + 屏幕空间武器

当前版本：
- HP / Score / Wave / Weapon
- 低血量全屏红闪
- Pistol / Shotgun 双武器显示
- Wave / Boss 提示文字
- Boss 血条
- Game Over 最终统计
"""

import math
import pygame

from settings import *


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 28)
        self.small_font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 78, bold=True)
        self.mid_font = pygame.font.SysFont("consolas", 48, bold=True)

    def draw_hud(
        self,
        screen,
        player,
        game_time=0.0,
        score=0,
        wave=1,
        weapon=WEAPON_PISTOL,
        map_name="",
        difficulty="NORMAL",
        shotgun_ammo=0,
        objective_text=""
    ):
        self.draw_low_health_flash(screen, player, game_time)
        self.draw_health(screen, player)
        self.draw_armor(screen, player)
        self.draw_score(screen, score, wave)
        self.draw_weapon_name(screen, weapon, shotgun_ammo)
        self.draw_map_name(screen, map_name)
        self.draw_difficulty_name(screen, difficulty)
        self.draw_objective(screen, objective_text)
        self.draw_crosshair(screen, weapon)

    def draw_low_health_flash(self, screen, player, game_time):
        if player.health > 30:
            return

        pulse = abs(math.sin(game_time * 7.0))
        alpha = int(35 + 55 * pulse)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def draw_health(self, screen, player):
        if player.health <= 30:
            color = COLOR_RED
        elif player.health <= 60:
            color = COLOR_YELLOW
        else:
            color = COLOR_WHITE

        hp_text = self.font.render(f"HP: {player.health}", True, color)
        screen.blit(hp_text, (20, 20))

    def draw_armor(self, screen, player):
        if player.armor <= 0:
            color = (95, 130, 160)
        elif player.armor < 50:
            color = (110, 180, 230)
        else:
            color = (120, 220, 255)

        armor_text = self.small_font.render(f"ARMOR: {player.armor}", True, color)
        screen.blit(armor_text, (20, 48))

    def draw_score(self, screen, score, wave):
        score_text = self.font.render(f"SCORE: {score}", True, COLOR_WHITE)
        wave_text = self.font.render(f"WAVE: {wave}", True, COLOR_WHITE)

        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
        screen.blit(wave_text, (SCREEN_WIDTH - wave_text.get_width() - 20, 55))

    def draw_weapon_name(self, screen, weapon, shotgun_ammo=0):
        if weapon == WEAPON_SHOTGUN:
            label = f"WEAPON: {weapon}  SHELLS: {shotgun_ammo}/{SHOTGUN_MAX_AMMO}"
        else:
            label = f"WEAPON: {weapon}  AMMO: INF"

        text = self.small_font.render(label, True, (220, 220, 220))
        screen.blit(text, (20, 76))

    def draw_map_name(self, screen, map_name):
        if not map_name:
            return

        text = self.small_font.render(f"MAP: {map_name}", True, (180, 220, 230))
        screen.blit(text, (20, 100))

    def draw_difficulty_name(self, screen, difficulty):
        text = self.small_font.render(f"DIFFICULTY: {difficulty}", True, (220, 205, 150))
        screen.blit(text, (20, 124))

    def draw_objective(self, screen, objective_text):
        if not objective_text:
            return

        text = self.small_font.render(objective_text, True, (235, 220, 150))
        x = SCREEN_WIDTH // 2 - text.get_width() // 2
        screen.blit(text, (x, 86))

    def draw_crosshair(self, screen, weapon=WEAPON_PISTOL):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        if weapon == WEAPON_SHOTGUN:
            size = 16
            gap = 9
            pygame.draw.circle(screen, COLOR_WHITE, (center_x, center_y), 18, 1)
        else:
            size = 10
            gap = 5

        pygame.draw.line(screen, COLOR_WHITE, (center_x - size - gap, center_y), (center_x - gap, center_y), 2)
        pygame.draw.line(screen, COLOR_WHITE, (center_x + gap, center_y), (center_x + size + gap, center_y), 2)
        pygame.draw.line(screen, COLOR_WHITE, (center_x, center_y - size - gap), (center_x, center_y - gap), 2)
        pygame.draw.line(screen, COLOR_WHITE, (center_x, center_y + gap), (center_x, center_y + size + gap), 2)
        pygame.draw.circle(screen, COLOR_WHITE, (center_x, center_y), 2)

    def draw_weapon(self, screen, recoil_timer, recoil_duration, moving, time_seconds, weapon=WEAPON_PISTOL):
        center_x = SCREEN_WIDTH // 2
        base_y = SCREEN_HEIGHT - 95

        bob_x = 0
        bob_y = 0

        if moving:
            bob_x = math.sin(time_seconds * 10.0) * 8
            bob_y = abs(math.sin(time_seconds * 10.0)) * 7

        recoil_ratio = 0.0

        if recoil_timer > 0 and recoil_duration > 0:
            recoil_ratio = recoil_timer / recoil_duration
            recoil_ratio = max(0.0, min(1.0, recoil_ratio))

        recoil_y = int(38 * recoil_ratio)
        recoil_x = int(-10 * recoil_ratio)

        gun_x = int(center_x + bob_x + recoil_x)
        gun_y = int(base_y + bob_y + recoil_y)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        if weapon == WEAPON_SHOTGUN:
            self.draw_shotgun_model(overlay, gun_x, gun_y, recoil_timer, recoil_duration, recoil_ratio)
        else:
            self.draw_pistol_model(overlay, gun_x, gun_y, recoil_timer, recoil_duration, recoil_ratio)

        screen.blit(overlay, (0, 0))

    def draw_pistol_model(self, overlay, gun_x, gun_y, recoil_timer, recoil_duration, recoil_ratio):
        pygame.draw.rect(overlay, (20, 20, 22, 230), (gun_x - 58, gun_y + 28, 116, 92), border_radius=12)
        pygame.draw.rect(overlay, (70, 70, 78, 255), (gun_x - 48, gun_y + 18, 96, 96), border_radius=10)
        pygame.draw.rect(overlay, (95, 95, 105, 255), (gun_x - 20, gun_y - 52, 40, 88), border_radius=8)
        pygame.draw.rect(overlay, (25, 25, 28, 255), (gun_x - 13, gun_y - 58, 26, 20), border_radius=5)
        pygame.draw.line(overlay, (150, 150, 160, 180), (gun_x - 34, gun_y + 30), (gun_x - 34, gun_y + 94), 3)
        pygame.draw.rect(overlay, (45, 45, 50, 255), (gun_x + 26, gun_y + 65, 38, 78), border_radius=8)

        if recoil_timer > recoil_duration * 0.45:
            self.draw_muzzle_flash(overlay, gun_x, gun_y - 65, recoil_ratio, shotgun=False)

    def draw_shotgun_model(self, overlay, gun_x, gun_y, recoil_timer, recoil_duration, recoil_ratio):
        pygame.draw.rect(overlay, (28, 22, 18, 245), (gun_x - 92, gun_y + 30, 184, 66), border_radius=12)
        pygame.draw.rect(overlay, (80, 50, 30, 255), (gun_x - 82, gun_y + 24, 164, 58), border_radius=10)
        pygame.draw.rect(overlay, (45, 45, 48, 255), (gun_x - 46, gun_y - 44, 92, 88), border_radius=10)
        pygame.draw.rect(overlay, (20, 20, 22, 255), (gun_x - 18, gun_y - 70, 16, 42), border_radius=4)
        pygame.draw.rect(overlay, (20, 20, 22, 255), (gun_x + 3, gun_y - 70, 16, 42), border_radius=4)
        pygame.draw.line(overlay, (150, 120, 80, 180), (gun_x - 70, gun_y + 43), (gun_x + 70, gun_y + 43), 4)

        if recoil_timer > recoil_duration * 0.55:
            self.draw_muzzle_flash(overlay, gun_x, gun_y - 75, recoil_ratio, shotgun=True)

    def draw_muzzle_flash(self, overlay, gun_x, muzzle_y, recoil_ratio, shotgun=False):
        flash_alpha = int(255 * recoil_ratio)
        radius = 48 if shotgun else 34
        pygame.draw.circle(overlay, (255, 230, 120, flash_alpha), (gun_x, muzzle_y), radius)
        pygame.draw.circle(overlay, (255, 120, 30, flash_alpha), (gun_x, muzzle_y), int(radius * 0.65))
        pygame.draw.polygon(
            overlay,
            (255, 245, 180, flash_alpha),
            [(gun_x, muzzle_y - radius - 20), (gun_x - radius // 2, muzzle_y - 12), (gun_x + radius // 2, muzzle_y - 12)]
        )

    def draw_boss_health(self, screen, boss):
        if boss is None or boss.dead:
            return

        bar_width = 500
        bar_height = 30
        x = SCREEN_WIDTH // 2 - bar_width // 2
        y = 30

        pygame.draw.rect(screen, COLOR_DARK_RED, (x, y, bar_width, bar_height))

        ratio = boss.health / boss.max_health
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(screen, COLOR_RED, (x, y, int(bar_width * ratio), bar_height))
        pygame.draw.rect(screen, COLOR_WHITE, (x, y, bar_width, bar_height), 2)

        text = self.font.render("BOSS", True, COLOR_WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y - 32))

    def draw_boss_warning(self, screen, boss):
        if boss is None or boss.dead or boss.state != "CHARGING":
            return

        progress = boss.get_charge_draw_ratio()
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.018)
        alpha = int(90 + 120 * pulse)

        warning = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(warning, (180, 20, 10, 55), (0, 0, SCREEN_WIDTH, 54))
        pygame.draw.rect(warning, (255, 70, 35, alpha), (0, 0, int(SCREEN_WIDTH * progress), 5))

        text = self.font.render("BOSS ATTACK INCOMING", True, (255, 230, 185))
        warning.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 15))

        screen.blit(warning, (0, 0))

    def draw_center_message(self, screen, title, subtitle="", timer=0.0, duration=1.0):
        if not title:
            return

        ratio = max(0.0, min(1.0, timer / max(duration, 0.01)))
        alpha = int(255 * min(1.0, ratio * 1.8))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(90 * ratio)))

        title_text = self.mid_font.render(title, True, COLOR_WHITE)
        title_text.set_alpha(alpha)
        overlay.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 70))

        if subtitle:
            sub_text = self.font.render(subtitle, True, (220, 220, 220))
            sub_text.set_alpha(alpha)
            overlay.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, SCREEN_HEIGHT // 2 - 18))

        screen.blit(overlay, (0, 0))

    def draw_minimap(
        self,
        screen,
        player,
        enemies,
        boss,
        portals,
        health_packs,
        armor_packs,
        ammo_packs,
        exit_portal_active=False
    ):
        scale = 5
        padding = 10
        map_size = MAP_SIZE * scale
        x0 = SCREEN_WIDTH - map_size - 22
        y0 = 96

        panel = pygame.Surface((map_size + padding * 2, map_size + padding * 2), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))

        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                rect = pygame.Rect(
                    padding + x * scale,
                    padding + y * scale,
                    scale,
                    scale
                )

                if WORLD_MAP[y][x] == 1 or (x, y) in PILLAR_SET:
                    pygame.draw.rect(panel, (120, 120, 120, 220), rect)
                else:
                    pygame.draw.rect(panel, (28, 28, 32, 190), rect)

        for portal in portals:
            self.draw_minimap_dot(panel, portal.x, portal.y, scale, padding, (190, 60, 255), 3)

        if exit_portal_active:
            self.draw_minimap_dot(
                panel,
                BOSS_PORTAL_POSITION[0],
                BOSS_PORTAL_POSITION[1],
                scale,
                padding,
                (120, 255, 180),
                5
            )

        for pack in health_packs:
            self.draw_minimap_dot(panel, pack.x, pack.y, scale, padding, (60, 230, 90), 3)

        for pack in armor_packs:
            self.draw_minimap_dot(panel, pack.x, pack.y, scale, padding, (80, 180, 255), 3)

        for pack in ammo_packs:
            self.draw_minimap_dot(panel, pack.x, pack.y, scale, padding, (235, 150, 50), 3)

        for enemy in enemies:
            if not enemy.dead:
                if enemy.__class__.__name__ == "FastDemon":
                    color = (255, 145, 45)
                else:
                    color = (255, 75, 55)

                self.draw_minimap_dot(panel, enemy.x, enemy.y, scale, padding, color, 3)

        if boss is not None and not boss.dead:
            self.draw_minimap_dot(panel, boss.x, boss.y, scale, padding, (255, 45, 210), 5)

        px = int(padding + player.x * scale)
        py = int(padding + player.y * scale)
        pygame.draw.circle(panel, (80, 210, 255), (px, py), 4)

        view_x = px + math.cos(player.angle) * 12
        view_y = py + math.sin(player.angle) * 12
        pygame.draw.line(panel, (80, 210, 255), (px, py), (view_x, view_y), 2)

        title = self.small_font.render("MAP", True, COLOR_WHITE)
        panel.blit(title, (padding, map_size + padding - 18))

        screen.blit(panel, (x0, y0))

    def draw_minimap_dot(self, panel, x, y, scale, padding, color, radius):
        pygame.draw.circle(
            panel,
            color,
            (int(padding + x * scale), int(padding + y * scale)),
            radius
        )

    def get_run_rank(self, score, bosses, wave, victory=False):
        if victory:
            return "SS"

        if score >= 5000 or bosses >= 3 or wave >= 4:
            return "S"

        if score >= 3000 or bosses >= 2 or wave >= 3:
            return "A"

        if score >= 1500 or bosses >= 1 or wave >= 2:
            return "B"

        return "C"

    def draw_pause_menu(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))

        title = self.big_font.render("PAUSED", True, COLOR_WHITE)
        lines = [
            "SPACE / ESC  Resume",
            "R            Restart",
            "Q            Main Menu",
            "",
            "WASD Move | Mouse Look | LMB/SPACE Shoot",
            "1 Pistol | 2 Shotgun | M Map | TAB Debug",
            "Goal: Keys -> Bosses -> Center EXIT",
        ]

        overlay.blit(
            title,
            (
                SCREEN_WIDTH // 2 - title.get_width() // 2,
                SCREEN_HEIGHT // 2 - 150,
            )
        )

        y = SCREEN_HEIGHT // 2 - 35
        for line in lines:
            if line == "":
                y += 20
                continue
            text = self.font.render(line, True, (220, 220, 220))
            overlay.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 36

        screen.blit(overlay, (0, 0))

    def draw_game_over(
        self,
        screen,
        score=0,
        kills=0,
        bosses=0,
        time_survived=0.0,
        wave=1,
        high_scores=None,
        victory=False
    ):
        title_text = "YOU WIN" if victory else "GAME OVER"
        title_color = (120, 255, 180) if victory else COLOR_RED
        title = self.big_font.render(title_text, True, title_color)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 150))

        rank = self.get_run_rank(score, bosses, wave, victory)

        stats = [
            f"RANK: {rank}",
            f"Final Score: {score}",
            f"Kills: {kills}",
            f"Bosses Defeated: {bosses}",
            f"Reached Wave: {wave}",
            f"Time Survived: {time_survived:.1f}s",
        ]

        if high_scores is not None:
            stats.extend([
                "",
                f"Best Score: {high_scores.get('score', 0)}",
                f"Best Wave: {high_scores.get('wave', 1)}",
                f"Best Time: {high_scores.get('time', 0.0):.1f}s",
                f"Wins: {high_scores.get('wins', 0)}",
            ])

        y = SCREEN_HEIGHT // 2 - 52
        for line in stats:
            if line == "":
                y += 14
                continue

            text = self.font.render(line, True, COLOR_WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 30

        tip = self.font.render("Press Any Key", True, COLOR_WHITE)
        screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, y + 20))

    def draw_menu(self, screen, difficulty="NORMAL"):
        title = self.big_font.render("DOOM-LIKE SURVIVAL", True, COLOR_PURPLE)
        tip = self.font.render("Press SPACE to Start", True, COLOR_WHITE)
        subtitle = self.small_font.render(
            "WASD Move | Mouse Look | LMB/SPACE Shoot | 1/2 Weapon | M Map | ESC Pause",
            True,
            (190, 190, 190)
        )
        objective_tip = self.small_font.render(
            "Clear waves, defeat 3 bosses, then escape through the center EXIT",
            True,
            (235, 220, 150)
        )
        difficulty_tip = self.small_font.render(
            f"Difficulty: {difficulty}   [1 Easy] [2 Normal] [3 Hard]",
            True,
            (225, 210, 150)
        )
        map_tip = self.small_font.render(
            "Each run loads a different 2.5D maze arena",
            True,
            (150, 205, 215)
        )

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 120))
        screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 + 55))
        screen.blit(objective_tip, (SCREEN_WIDTH // 2 - objective_tip.get_width() // 2, SCREEN_HEIGHT // 2 + 84))
        screen.blit(difficulty_tip, (SCREEN_WIDTH // 2 - difficulty_tip.get_width() // 2, SCREEN_HEIGHT // 2 + 113))
        screen.blit(map_tip, (SCREEN_WIDTH // 2 - map_tip.get_width() // 2, SCREEN_HEIGHT // 2 + 142))
