"""
main.py
Survival 积分制版本 + 双武器 + Portal 素材 + Wave Scaling + Health Pack + Boss 死亡动画 + Wave/Boss 提示。
"""

import os
import math
import random
import json
import pygame

from settings import *
from player import Player
from enemy import Enemy, FastDemon, Boss, is_large_sprite_fully_blocked
from portal import Portal
from world import World
from effects import (
    FireballExplosion,
    BossDeathExplosion,
    HealthPack,
    ArmorPack,
    AmmoPack,
    draw_damage_flash,
    draw_damage_vignette,
)
from ui import UI


MENU = "MENU"
PLAYING = "PLAYING"
PAUSED = "PAUSED"
GAME_OVER = "GAME_OVER"
WIN = "WIN"

MOUSE_SENSITIVITY = 0.003

PORTAL_TOTAL_TIME = 6.0
PORTAL_SPAWN_TIME = 3.0
ENEMY_FREEZE_AFTER_SPAWN = 2.0

BOSS_PORTAL_TOTAL_TIME = 7.0
BOSS_PORTAL_SPAWN_TIME = 3.5
BOSS_FREEZE_AFTER_SPAWN = 1.5

NEXT_WAVE_DELAY = 2.0

SHOOT_FLASH_DURATION = 0.10
SHOTGUN_FLASH_DURATION = 0.14

SHAKE_DURATION = 0.28
SHAKE_POWER = 10

HIT_SHAKE_DURATION = 0.08
HIT_SHAKE_POWER = 4

BOSS_APPEAR_SHAKE_DURATION = 0.45
BOSS_APPEAR_SHAKE_POWER = 7

FIREBALL_HIT_SHAKE_DURATION = 0.25
FIREBALL_HIT_SHAKE_POWER = 9

WEAPON_RECOIL_DURATION = 0.16
SHOTGUN_RECOIL_DURATION = 0.24

SCORE_IMP = 100
SCORE_FAST_DEMON = 75
SCORE_BOSS = 1000
SCORE_WAVE_CLEAR = 250

ANNOUNCE_DURATION = 1.6
WIN_BOSSES_REQUIRED = 3
EXIT_PORTAL_RADIUS = 0.75

HIGHSCORE_FILE = data_path("highscore.json")

DIFFICULTY_PRESETS = {
    "EASY": {
        "enemy_health": 0.85,
        "enemy_speed": 0.90,
        "enemy_damage": 0.75,
        "boss_health": 0.85,
        "boss_speed": 0.90,
        "boss_damage": 0.80,
        "health_drop": 1.35,
        "score": 0.85,
    },
    "NORMAL": {
        "enemy_health": 1.00,
        "enemy_speed": 1.00,
        "enemy_damage": 1.00,
        "boss_health": 1.00,
        "boss_speed": 1.00,
        "boss_damage": 1.00,
        "health_drop": 1.00,
        "score": 1.00,
    },
    "HARD": {
        "enemy_health": 1.25,
        "enemy_speed": 1.15,
        "enemy_damage": 1.30,
        "boss_health": 1.25,
        "boss_speed": 1.12,
        "boss_damage": 1.25,
        "health_drop": 0.75,
        "score": 1.25,
    },
}

DIFFICULTY_KEYS = {
    pygame.K_1: "EASY",
    pygame.K_2: "NORMAL",
    pygame.K_3: "HARD",
}


class KeyState:
    def __init__(self, pressed_keys):
        self.pressed_keys = pressed_keys

    def __getitem__(self, key):
        return key in self.pressed_keys


class Game:
    def __init__(self):
        pygame.init()

        self.audio_enabled = True
        try:
            pygame.mixer.init()
        except pygame.error:
            self.audio_enabled = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Doom-like Survival")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU

        self.ui = UI()
        self.sounds = {}
        self.load_sounds()

        self.player = Player()
        self.world = World()

        self.enemies = []
        self.portals = []
        self.health_packs = []
        self.armor_packs = []
        self.ammo_packs = []

        self.boss = None
        self.boss_portal_created = False
        self.boss_enrage_announced = False
        self.exit_portal_active = False

        self.fireballs = []
        self.explosions = []
        self.boss_death_effects = []

        self.score = 0
        self.kills = 0
        self.bosses_defeated = 0
        self.wave = 1
        self.next_wave_timer = 0.0
        self.map_name = MAP_PRESETS[0]["name"]
        self.difficulty = "NORMAL"

        self.current_weapon = WEAPON_PISTOL
        self.shotgun_ammo = SHOTGUN_START_AMMO

        self.pressed_keys = set()
        self.debug_font = pygame.font.SysFont("consolas", 20)
        self.show_debug = False
        self.show_minimap = False

        self.shoot_flash_timer = 0.0
        self.shoot_flash_hit = False
        self.shoot_flash_lines = []

        self.weapon_recoil_timer = 0.0
        self.weapon_recoil_duration = WEAPON_RECOIL_DURATION

        self.shake_timer = 0.0
        self.shake_power = SHAKE_POWER
        self.shake_duration = SHAKE_DURATION

        self.game_time = 0.0
        self.announce_title = ""
        self.announce_subtitle = ""
        self.announce_timer = 0.0
        self.announce_duration = ANNOUNCE_DURATION

        self.high_scores = self.load_high_scores()

    def load_sounds(self):
        if not self.audio_enabled:
            return

        sound_files = {
            "shoot": sound_path("shoot.wav"),
            "shotgun": sound_path("shotgun.wav"),
            "pickup": sound_path("pickup.wav"),
            "hurt": sound_path("hurt.wav"),
            "death": sound_path("death.wav"),
            "boss_appear": sound_path("boss_appear.wav"),
            "enemy_hit": sound_path("enemy_hit.wav"),
            "fireball": sound_path("fireball.wav"),
            "explosion": sound_path("explosion.wav"),
        }

        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def load_high_scores(self):
        default_scores = {
            "score": 0,
            "wave": 1,
            "kills": 0,
            "bosses": 0,
            "time": 0.0,
            "wins": 0,
        }

        if not os.path.exists(HIGHSCORE_FILE):
            return default_scores

        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return default_scores

        for key, value in default_scores.items():
            data.setdefault(key, value)

        return data

    def save_high_scores(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as file:
                json.dump(self.high_scores, file, indent=2)
        except OSError:
            pass

    def update_high_scores(self, victory=False):
        self.high_scores["score"] = max(self.high_scores["score"], self.score)
        self.high_scores["wave"] = max(self.high_scores["wave"], self.wave)
        self.high_scores["kills"] = max(self.high_scores["kills"], self.kills)
        self.high_scores["bosses"] = max(self.high_scores["bosses"], self.bosses_defeated)
        self.high_scores["time"] = max(self.high_scores["time"], round(self.game_time, 1))

        if victory:
            self.high_scores["wins"] += 1

        self.save_high_scores()

    def finish_game(self, result_state):
        if self.state != PLAYING:
            return

        self.update_high_scores(victory=(result_state == WIN))
        self.state = result_state

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def reset_game(self):
        self.map_name = choose_random_map_preset()
        self.player = Player()
        self.world = World()

        self.enemies = []
        self.portals = []
        self.health_packs = []
        self.armor_packs = []
        self.ammo_packs = []

        self.boss = None
        self.boss_portal_created = False
        self.boss_enrage_announced = False
        self.exit_portal_active = False

        self.fireballs = []
        self.explosions = []
        self.boss_death_effects = []

        self.score = 0
        self.kills = 0
        self.bosses_defeated = 0
        self.wave = 1
        self.next_wave_timer = 0.0

        self.current_weapon = WEAPON_PISTOL
        self.shotgun_ammo = SHOTGUN_START_AMMO
        self.pressed_keys.clear()
        self.show_minimap = False

        self.shoot_flash_timer = 0.0
        self.shoot_flash_hit = False
        self.shoot_flash_lines = []
        self.weapon_recoil_timer = 0.0
        self.weapon_recoil_duration = WEAPON_RECOIL_DURATION

        self.shake_timer = 0.0
        self.shake_power = SHAKE_POWER
        self.shake_duration = SHAKE_DURATION

        self.game_time = 0.0
        self.show_announcement("SURVIVE", "Clear waves and defeat 3 bosses to open the EXIT", 2.2)
        self.spawn_enemy_wave()

    def show_announcement(self, title, subtitle="", duration=ANNOUNCE_DURATION):
        self.announce_title = title
        self.announce_subtitle = subtitle
        self.announce_duration = duration
        self.announce_timer = duration

    def get_wave_score_multiplier(self):
        difficulty_score = DIFFICULTY_PRESETS[self.difficulty]["score"]
        wave_score = 1.0 + max(0, self.wave - 1) * WAVE_SCORE_GROWTH
        return wave_score * difficulty_score

    def get_scaled_score(self, base_score):
        return int(base_score * self.get_wave_score_multiplier())

    def spawn_enemy_wave(self):
        self.boss = None
        self.boss_portal_created = False
        self.fireballs = []
        self.explosions = []

        positions = list(ENEMY_PORTAL_POSITIONS)
        extra_count = min(4, max(0, self.wave - 1))

        for i in range(extra_count):
            positions.append(random.choice(ENEMY_PORTAL_POSITIONS))

        for x, y in positions:
            self.portals.append(
                Portal(
                    x,
                    y,
                    PORTAL_SMALL_RADIUS,
                    PORTAL_TOTAL_TIME,
                    self.spawn_wave_enemy,
                    spawn_time=PORTAL_SPAWN_TIME,
                )
            )

    def enter_game(self):
        self.reset_game()
        self.state = PLAYING

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

    def restart_game(self):
        self.reset_game()
        self.state = PLAYING

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

    def pause_game(self):
        self.state = PAUSED
        self.pressed_keys.clear()

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def resume_game(self):
        self.state = PLAYING
        self.pressed_keys.clear()

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

    def return_menu(self):
        self.state = MENU
        self.pressed_keys.clear()

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def spawn_enemy(self, x, y):
        enemy = Enemy(x, y)
        enemy.apply_wave_scaling(self.wave)
        self.apply_enemy_difficulty(enemy)
        enemy.freeze_timer = ENEMY_FREEZE_AFTER_SPAWN
        enemy.spawn_visual_timer = 1.0
        enemy.spawn_visual_duration = 1.0
        self.enemies.append(enemy)

    def spawn_fast_demon(self, x, y):
        demon = FastDemon(x, y)
        demon.apply_wave_scaling(self.wave)
        self.apply_enemy_difficulty(demon)
        demon.freeze_timer = ENEMY_FREEZE_AFTER_SPAWN * 0.75
        demon.spawn_visual_timer = 0.8
        demon.spawn_visual_duration = 0.8
        self.enemies.append(demon)

    def spawn_wave_enemy(self, x, y):
        fast_chance = min(0.45, max(0.0, (self.wave - 1) * 0.16))

        if random.random() < fast_chance:
            self.spawn_fast_demon(x, y)
        else:
            self.spawn_enemy(x, y)

    def spawn_boss(self, x, y):
        self.boss = Boss(x, y)
        self.boss.apply_wave_scaling(self.wave)
        self.apply_boss_difficulty(self.boss)
        self.boss_enrage_announced = False
        self.boss.freeze_timer = BOSS_FREEZE_AFTER_SPAWN
        self.boss.spawn_visual_timer = 1.4
        self.boss.spawn_visual_duration = 1.4

        self.start_screen_shake(BOSS_APPEAR_SHAKE_DURATION, BOSS_APPEAR_SHAKE_POWER)
        self.play_sound("boss_appear")
        self.show_announcement("BOSS INCOMING", "Defeat it to reach the next wave", 1.8)

    def apply_enemy_difficulty(self, enemy):
        preset = DIFFICULTY_PRESETS[self.difficulty]
        enemy.health = max(1, int(enemy.health * preset["enemy_health"]))
        enemy.speed *= preset["enemy_speed"]
        enemy.damage = max(1, int(enemy.damage * preset["enemy_damage"]))

    def apply_boss_difficulty(self, boss):
        preset = DIFFICULTY_PRESETS[self.difficulty]
        boss.max_health = max(1, int(boss.max_health * preset["boss_health"]))
        boss.health = boss.max_health
        boss.speed *= preset["boss_speed"]
        boss.damage = max(1, int(boss.damage * preset["boss_damage"]))

    def maybe_spawn_boss_portal(self):
        if self.next_wave_timer > 0:
            return
        if self.exit_portal_active:
            return
        if self.boss_portal_created:
            return
        if self.boss is not None:
            return
        if len(self.enemies) > 0:
            return
        if len(self.portals) > 0:
            return

        self.create_boss_portal()

    def create_boss_portal(self):
        if self.boss_portal_created:
            return

        self.boss_portal_created = True
        x, y = BOSS_PORTAL_POSITION

        self.portals.append(
            Portal(
                x,
                y,
                PORTAL_BIG_RADIUS,
                BOSS_PORTAL_TOTAL_TIME,
                self.spawn_boss,
                spawn_time=BOSS_PORTAL_SPAWN_TIME,
            )
        )

        self.start_screen_shake(BOSS_APPEAR_SHAKE_DURATION, BOSS_APPEAR_SHAKE_POWER)
        self.show_announcement("BOSS PORTAL", "Get ready", 1.4)

    def force_boss_phase(self):
        self.enemies = []
        self.portals = []
        self.fireballs = []
        self.explosions = []
        self.boss = None
        self.boss_portal_created = False
        self.boss_enrage_announced = False
        self.exit_portal_active = False
        self.next_wave_timer = 0.0
        self.create_boss_portal()
        print("DEBUG: forced boss portal phase")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)

                if self.state == MENU:
                    if event.key == pygame.K_SPACE:
                        self.enter_game()
                    elif event.key in DIFFICULTY_KEYS:
                        self.difficulty = DIFFICULTY_KEYS[event.key]

                elif self.state == PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_game()
                    elif event.key == pygame.K_SPACE:
                        self.player_shoot()
                    elif event.key == pygame.K_1:
                        self.current_weapon = WEAPON_PISTOL
                        self.show_announcement("PISTOL", "Fast and accurate", 0.8)
                    elif event.key == pygame.K_2:
                        self.current_weapon = WEAPON_SHOTGUN
                        self.show_announcement("SHOTGUN", "Close-range burst damage", 0.8)
                    elif event.key == pygame.K_n:
                        self.force_boss_phase()
                    elif event.key == pygame.K_TAB:
                        self.show_debug = not self.show_debug
                    elif event.key == pygame.K_m:
                        self.show_minimap = not self.show_minimap

                elif self.state == PAUSED:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                        self.resume_game()
                    elif event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        self.return_menu()

                elif self.state in (GAME_OVER, WIN):
                    self.return_menu()

            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)

            elif event.type == pygame.MOUSEMOTION:
                if self.state == PLAYING:
                    mouse_dx = event.rel[0]
                    self.player.angle += mouse_dx * MOUSE_SENSITIVITY
                    self.player.angle = self.normalize_angle(self.player.angle)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == PLAYING and event.button == 1:
                    self.player_shoot()
                elif self.state == PAUSED and event.button == 1:
                    self.resume_game()
                elif self.state in (GAME_OVER, WIN):
                    self.return_menu()

    def update(self, dt):
        if self.state != PLAYING:
            return

        self.game_time += dt

        keys = KeyState(self.pressed_keys)
        self.player.update(dt, keys)

        for portal in self.portals:
            portal.update(dt)
        self.portals = [p for p in self.portals if not p.finished]

        for enemy in self.enemies:
            self.update_enemy(enemy, dt)
        self.enemies = [e for e in self.enemies if not e.dead]

        self.maybe_spawn_boss_portal()
        self.update_boss(dt)
        self.update_fireballs(dt)
        self.update_explosions(dt)
        self.update_health_packs(dt)
        self.update_armor_packs(dt)
        self.update_ammo_packs(dt)
        self.update_exit_portal()
        self.update_next_wave(dt)

        if self.shoot_flash_timer > 0:
            self.shoot_flash_timer -= dt
        if self.weapon_recoil_timer > 0:
            self.weapon_recoil_timer -= dt
        if self.shake_timer > 0:
            self.shake_timer -= dt
        if self.announce_timer > 0:
            self.announce_timer -= dt

        if self.player.is_dead():
            self.finish_game(GAME_OVER)

    def update_exit_portal(self):
        if not self.exit_portal_active:
            return

        dx = self.player.x - BOSS_PORTAL_POSITION[0]
        dy = self.player.y - BOSS_PORTAL_POSITION[1]

        if math.hypot(dx, dy) <= EXIT_PORTAL_RADIUS:
            self.finish_game(WIN)

    def update_next_wave(self, dt):
        if self.next_wave_timer <= 0:
            return

        self.next_wave_timer -= dt

        if self.next_wave_timer <= 0:
            self.wave += 1
            self.show_announcement(f"WAVE {self.wave}", "Enemies are getting stronger", 1.6)
            self.spawn_enemy_wave()

    def update_enemy(self, enemy, dt):
        if enemy.dead:
            return

        old_health = self.player.health
        enemy.update(dt, self.player)

        if self.player.health < old_health:
            self.start_screen_shake(SHAKE_DURATION, SHAKE_POWER)
            self.play_sound("hurt")

    def update_boss(self, dt):
        if self.boss is None:
            return

        if self.boss.dead:
            self.score += self.get_scaled_score(SCORE_BOSS + SCORE_WAVE_CLEAR)
            self.bosses_defeated += 1
            self.boss_death_effects.append(BossDeathExplosion(self.boss.x, self.boss.y))

            self.boss = None
            self.fireballs = []
            self.explosions = []
            self.boss_enrage_announced = False

            if self.bosses_defeated >= WIN_BOSSES_REQUIRED:
                self.exit_portal_active = True
                self.next_wave_timer = 0.0
                self.show_announcement("EXIT OPENED", "Return to the center portal", 2.2)
            else:
                self.next_wave_timer = NEXT_WAVE_DELAY
                remaining = WIN_BOSSES_REQUIRED - self.bosses_defeated
                self.show_announcement("BOSS DEFEATED", f"{remaining} boss fights left", 1.5)

            self.start_screen_shake(0.65, 13)
            self.play_sound("explosion")
            print("boss defeated, score:", self.score)
            return

        old_fireball_count = len(self.fireballs)
        self.boss.update(dt, self.player, self.fireballs, play_sound=self.play_sound)

        if (
            not self.boss_enrage_announced
            and
            self.boss.get_health_ratio() <= 0.55
        ):
            self.boss_enrage_announced = True
            self.start_screen_shake(0.35, 8)
            self.show_announcement("BOSS ENRAGED", "Attacks are faster and denser", 1.4)

        if len(self.fireballs) > old_fireball_count:
            self.start_screen_shake(0.10, 3)

    def update_fireballs(self, dt):
        for fireball in self.fireballs:
            old_health = self.player.health
            result = fireball.update(dt, self.player)

            if result == "wall":
                self.explosions.append(FireballExplosion(fireball.x, fireball.y))
                self.play_sound("explosion")

            elif result == "player":
                self.explosions.append(FireballExplosion(fireball.x, fireball.y))

                if self.player.health < old_health:
                    self.start_screen_shake(FIREBALL_HIT_SHAKE_DURATION, FIREBALL_HIT_SHAKE_POWER)
                    self.play_sound("hurt")

        self.fireballs = [f for f in self.fireballs if f.active]

    def update_explosions(self, dt):
        for explosion in self.explosions:
            explosion.update(dt)
        self.explosions = [e for e in self.explosions if not e.finished]

        for effect in self.boss_death_effects:
            effect.update(dt)
        self.boss_death_effects = [e for e in self.boss_death_effects if not e.finished]

    def update_health_packs(self, dt):
        for pack in self.health_packs:
            picked = pack.update(dt, self.player)
            if picked:
                self.play_sound("pickup")

        self.health_packs = [p for p in self.health_packs if p.active]

    def update_armor_packs(self, dt):
        for pack in self.armor_packs:
            picked = pack.update(dt, self.player)
            if picked:
                self.play_sound("pickup")

        self.armor_packs = [p for p in self.armor_packs if p.active]

    def update_ammo_packs(self, dt):
        for pack in self.ammo_packs:
            picked = pack.update(dt, self)

            if picked:
                self.play_sound("pickup")
                self.show_announcement("SHELLS", f"+{pack.ammo_amount} shotgun ammo", 0.9)

        self.ammo_packs = [p for p in self.ammo_packs if p.active]

    def get_objective_text(self):
        if self.exit_portal_active:
            return "OBJECTIVE: Enter the center EXIT"

        remaining_bosses = max(0, WIN_BOSSES_REQUIRED - self.bosses_defeated)
        if remaining_bosses > 0:
            return f"OBJECTIVE: Defeat bosses ({self.bosses_defeated}/{WIN_BOSSES_REQUIRED})"

        return "OBJECTIVE: Survive"

    def start_screen_shake(self, duration, power):
        if duration >= self.shake_timer:
            self.shake_timer = duration
            self.shake_duration = duration
            self.shake_power = power

    def apply_weapon_knockback(self, strength):
        back_x = -math.cos(self.player.angle)
        back_y = -math.sin(self.player.angle)
        self.player.try_move(self.player.x + back_x * strength, self.player.y + back_y * strength)

    def player_shoot(self):
        if not self.player.can_shoot():
            return

        if self.current_weapon == WEAPON_SHOTGUN:
            self.shoot_shotgun()
        else:
            self.shoot_pistol()

    def shoot_pistol(self):
        self.player.reset_shoot_timer(PISTOL_COOLDOWN)
        self.play_sound("shoot")

        self.weapon_recoil_timer = WEAPON_RECOIL_DURATION
        self.weapon_recoil_duration = WEAPON_RECOIL_DURATION
        self.apply_weapon_knockback(PISTOL_KNOCKBACK)

        target = self.find_shoot_target_at(0.0)
        self.shoot_flash_timer = SHOOT_FLASH_DURATION
        self.shoot_flash_hit = target is not None
        self.shoot_flash_lines = [0.0]

        if target is not None:
            self.damage_target(target, PISTOL_DAMAGE)
        else:
            print("shoot miss")

    def shoot_shotgun(self):
        if self.shotgun_ammo <= 0:
            self.current_weapon = WEAPON_PISTOL
            self.player.reset_shoot_timer(0.25)
            self.show_announcement("NO SHELLS", "Switched to pistol", 0.9)
            return

        self.player.reset_shoot_timer(SHOTGUN_COOLDOWN)
        self.shotgun_ammo -= 1
        self.play_sound("shotgun")
        if "shotgun" not in self.sounds:
            self.play_sound("shoot")

        self.weapon_recoil_timer = SHOTGUN_RECOIL_DURATION
        self.weapon_recoil_duration = SHOTGUN_RECOIL_DURATION
        self.apply_weapon_knockback(SHOTGUN_KNOCKBACK)

        offsets = []
        for i in range(SHOTGUN_PELLETS):
            if SHOTGUN_PELLETS == 1:
                offset = 0.0
            else:
                t = i / (SHOTGUN_PELLETS - 1)
                offset = -SHOTGUN_SPREAD + t * SHOTGUN_SPREAD * 2
            offset += random.uniform(-0.018, 0.018)
            offsets.append(offset)

        hit_any = False
        damaged_targets = []

        for offset in offsets:
            target = self.find_shoot_target_at(offset)
            if target is not None:
                hit_any = True
                self.damage_target(target, SHOTGUN_PELLET_DAMAGE)
                damaged_targets.append(target)

        self.shoot_flash_timer = SHOTGUN_FLASH_DURATION
        self.shoot_flash_hit = hit_any
        self.shoot_flash_lines = offsets

        if hit_any:
            print("shotgun hit pellets:", len(damaged_targets))
        else:
            print("shotgun miss")

    def damage_target(self, target, damage):
        already_dead = target.dead
        target.take_damage(damage)

        self.start_screen_shake(HIT_SHAKE_DURATION, HIT_SHAKE_POWER)
        self.play_sound("enemy_hit")

        print("hit target, hp:", target.health)

        if target.dead and not already_dead:
            print("target dead")
            self.play_sound("death")

            if isinstance(target, Enemy):
                self.handle_enemy_killed(target)

    def handle_enemy_killed(self, enemy):
        if isinstance(enemy, FastDemon):
            self.score += self.get_scaled_score(SCORE_FAST_DEMON)
        else:
            self.score += self.get_scaled_score(SCORE_IMP)

        self.kills += 1
        self.try_drop_health_pack(enemy.x, enemy.y)
        self.try_drop_armor_pack(enemy.x, enemy.y)
        self.try_drop_ammo_pack(enemy.x, enemy.y)

    def try_drop_health_pack(self, x, y):
        drop_chance = HEALTH_PACK_DROP_CHANCE * DIFFICULTY_PRESETS[self.difficulty]["health_drop"]

        if random.random() > drop_chance:
            return

        if is_wall(x, y):
            return

        self.health_packs.append(HealthPack(x, y))

    def try_drop_armor_pack(self, x, y):
        if random.random() > ARMOR_PACK_DROP_CHANCE:
            return

        if is_wall(x, y):
            return

        self.armor_packs.append(ArmorPack(x, y))

    def try_drop_ammo_pack(self, x, y):
        if random.random() > AMMO_PACK_DROP_CHANCE:
            return

        if is_wall(x, y):
            return

        self.ammo_packs.append(AmmoPack(x, y))

    def find_shoot_target_at(self, angle_offset=0.0):
        best_target = None
        best_distance = float("inf")
        targets = []

        for enemy in self.enemies:
            if not enemy.dead:
                targets.append(enemy)

        if self.boss is not None and not self.boss.dead:
            targets.append(self.boss)

        crosshair = (
            int(SCREEN_WIDTH // 2 + (angle_offset / HALF_FOV) * (SCREEN_WIDTH // 2)),
            SCREEN_HEIGHT // 2
        )

        for target in targets:
            dx = target.x - self.player.x
            dy = target.y - self.player.y
            distance = math.hypot(dx, dy)

            if isinstance(target, Boss):
                if is_large_sprite_fully_blocked(self.player, target.x, target.y, target.radius):
                    continue
            else:
                if self.is_wall_between(target.x, target.y):
                    continue

            if hasattr(target, "get_screen_hitbox"):
                rect = target.get_screen_hitbox(self.player)
                if rect is None:
                    continue
                if not rect.collidepoint(crosshair):
                    continue
            else:
                angle_to_target = math.atan2(dy, dx)
                diff = self.normalize_angle(angle_to_target - self.player.angle - angle_offset)
                dynamic_threshold = max(0.012, (target.radius * 1.8) / max(distance, 1.0))
                if abs(diff) > dynamic_threshold:
                    continue

            if distance < best_distance:
                best_distance = distance
                best_target = target

        return best_target

    def is_wall_between(self, target_x, target_y):
        return is_blocked(self.player.x, self.player.y, target_x, target_y)

    def get_nearest_enemy_debug_text(self):
        if len(self.enemies) <= 0:
            return "none"

        nearest = None
        nearest_dist = float("inf")
        nearest_diff = 0.0

        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.hypot(dx, dy)

            if dist < nearest_dist:
                nearest = enemy
                nearest_dist = dist
                angle_to_enemy = math.atan2(dy, dx)
                nearest_diff = self.normalize_angle(angle_to_enemy - self.player.angle)

        if nearest is None:
            return "none"

        if abs(nearest_diff) < math.pi / 4:
            direction = "FRONT"
        elif abs(nearest_diff) > math.pi * 3 / 4:
            direction = "BACK"
        elif nearest_diff > 0:
            direction = "RIGHT"
        else:
            direction = "LEFT"

        blocked_text = "blocked" if self.is_wall_between(nearest.x, nearest.y) else "visible"
        return f"{direction}, dist={nearest_dist:.1f}, pos=({nearest.x:.1f},{nearest.y:.1f}), {blocked_text}"

    def get_screen_shake_offset(self):
        if self.shake_timer <= 0:
            return 0, 0

        strength = self.shake_timer / self.shake_duration
        power = int(self.shake_power * strength)

        if power <= 0:
            return 0, 0

        return random.randint(-power, power), random.randint(-power, power)

    def is_player_moving(self):
        return (
            pygame.K_w in self.pressed_keys
            or pygame.K_a in self.pressed_keys
            or pygame.K_s in self.pressed_keys
            or pygame.K_d in self.pressed_keys
        )

    def draw_debug_text(self):
        if not self.show_debug:
            return

        boss_text = "none"
        if self.boss is not None:
            boss_text = f"{self.boss.health}/{self.boss.max_health}"

        lines = [
            f"HP = {self.player.health}",
            f"armor = {self.player.armor}",
            f"score = {self.score}",
            f"wave = {self.wave}",
            f"weapon = {self.current_weapon}",
            f"shotgun ammo = {self.shotgun_ammo}/{SHOTGUN_MAX_AMMO}",
            f"difficulty = {self.difficulty}",
            f"kills = {self.kills}",
            f"bosses = {self.bosses_defeated}",
            f"map = {self.map_name}",
            f"minimap = {self.show_minimap}",
            f"exit = {self.exit_portal_active}",
            f"time = {self.game_time:.1f}",
            f"x = {self.player.x:.2f}",
            f"y = {self.player.y:.2f}",
            f"enemies = {len(self.enemies)}",
            f"fast demons = {sum(1 for e in self.enemies if isinstance(e, FastDemon))}",
            f"nearest enemy = {self.get_nearest_enemy_debug_text()}",
            f"portals = {len(self.portals)}",
            f"health packs = {len(self.health_packs)}",
            f"armor packs = {len(self.armor_packs)}",
            f"ammo packs = {len(self.ammo_packs)}",
            f"fireballs = {len(self.fireballs)}",
            f"boss = {boss_text}",
            "1 = pistol | 2 = shotgun",
            "M = minimap on/off",
            "TAB = debug on/off",
            "DEBUG: N = force boss portal",
        ]

        padding = 10
        line_h = 22
        width = 650
        height = padding * 2 + line_h * len(lines)

        debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        debug_surface.fill((0, 0, 0, 145))

        y = padding
        for line in lines:
            text = self.debug_font.render(line, True, COLOR_WHITE)
            debug_surface.blit(text, (padding, y))
            y += line_h

        self.screen.blit(debug_surface, (16, 16))

    def draw_shoot_flash(self):
        if self.shoot_flash_timer <= 0:
            return

        alpha = int(255 * (self.shoot_flash_timer / max(SHOOT_FLASH_DURATION, 0.01)))
        if self.current_weapon == WEAPON_SHOTGUN:
            alpha = int(255 * (self.shoot_flash_timer / max(SHOTGUN_FLASH_DURATION, 0.01)))
        alpha = max(0, min(255, alpha))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        start = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125)

        if not self.shoot_flash_lines:
            self.shoot_flash_lines = [0.0]

        for offset in self.shoot_flash_lines:
            end_x = int(SCREEN_WIDTH // 2 + (offset / HALF_FOV) * (SCREEN_WIDTH // 2))
            end = (end_x, SCREEN_HEIGHT // 2)
            width1 = 6 if self.current_weapon == WEAPON_SHOTGUN else 8
            width2 = 3 if self.current_weapon == WEAPON_SHOTGUN else 4
            pygame.draw.line(overlay, (255, 255, 180, alpha), start, end, width1)
            pygame.draw.line(overlay, (255, 180, 40, alpha), start, end, width2)

        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.circle(overlay, (255, 255, 180, alpha), center, 15, 3)

        if self.shoot_flash_hit:
            pygame.draw.circle(overlay, (255, 60, 40, alpha), center, 24, 5)
            pygame.draw.circle(overlay, (255, 230, 160, alpha), center, 9)

        self.screen.blit(overlay, (0, 0))

    def draw_game_view(self):
        view = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.world.render(view, self.player)

        for portal in self.portals:
            portal.draw(view, self.player)

        if self.boss is not None:
            self.boss.draw(view, self.player)

        for enemy in self.enemies:
            enemy.draw(view, self.player)

        for pack in self.health_packs:
            pack.draw(view, self.player)

        for pack in self.armor_packs:
            pack.draw(view, self.player)

        for pack in self.ammo_packs:
            pack.draw(view, self.player)

        for fireball in self.fireballs:
            fireball.draw(view, self.player)

        for explosion in self.explosions:
            explosion.draw(view, self.player)

        for effect in self.boss_death_effects:
            effect.draw(view, self.player)

        if self.exit_portal_active:
            self.draw_exit_portal(view)

        self.draw_shoot_flash_on_surface(view)

        self.ui.draw_weapon(
            view,
            self.weapon_recoil_timer,
            self.weapon_recoil_duration,
            self.is_player_moving(),
            self.game_time,
            self.current_weapon
        )

        self.ui.draw_hud(
            view,
            self.player,
            self.game_time,
            self.score,
            self.wave,
            self.current_weapon,
            self.map_name,
            self.difficulty,
            self.shotgun_ammo,
            self.get_objective_text(),
        )

        if self.boss is not None and not self.boss.dead:
            self.ui.draw_boss_health(view, self.boss)
            self.ui.draw_boss_warning(view, self.boss)

        if self.show_minimap:
            self.ui.draw_minimap(
                view,
                self.player,
                self.enemies,
                self.boss,
                self.portals,
                self.health_packs,
                self.armor_packs,
                self.ammo_packs,
                self.exit_portal_active,
            )

        if self.announce_timer > 0:
            self.ui.draw_center_message(
                view,
                self.announce_title,
                self.announce_subtitle,
                self.announce_timer,
                self.announce_duration
            )

        self.draw_debug_text_on_surface(view)
        draw_damage_flash(view, self.player)
        draw_damage_vignette(view, self.player)

        offset_x, offset_y = self.get_screen_shake_offset()
        self.screen.blit(view, (offset_x, offset_y))

    def draw_exit_portal(self, surface):
        obj_x, obj_y = BOSS_PORTAL_POSITION
        dx = obj_x - self.player.x
        dy = obj_y - self.player.y
        distance = math.hypot(dx, dy)

        if distance <= 0.01:
            return

        angle_to_portal = math.atan2(dy, dx)
        angle_diff = self.normalize_angle(angle_to_portal - self.player.angle)

        if abs(angle_diff) > HALF_FOV:
            return

        if self.is_wall_between(obj_x, obj_y):
            return

        screen_x = SCREEN_WIDTH // 2 + (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2)
        size = int(0.95 * SCREEN_HEIGHT / max(distance, 0.65))
        size = max(28, min(size, 260))
        screen_y = SCREEN_HEIGHT // 2 + size // 3

        pulse = 0.5 + 0.5 * math.sin(self.game_time * 7.0)
        alpha = int(130 + 90 * pulse)

        portal_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        cx = portal_surface.get_width() // 2
        cy = portal_surface.get_height() // 2

        pygame.draw.circle(portal_surface, (60, 220, 130, alpha // 2), (cx, cy), size)
        pygame.draw.circle(portal_surface, (120, 255, 180, alpha), (cx, cy), int(size * 0.72), max(4, size // 12))
        pygame.draw.circle(portal_surface, (235, 255, 220, alpha), (cx, cy), int(size * 0.33))

        label = self.ui.small_font.render("EXIT", True, COLOR_WHITE)
        portal_surface.blit(label, (cx - label.get_width() // 2, cy - size - 8))

        surface.blit(portal_surface, (int(screen_x - cx), int(screen_y - cy)))

    def draw_shoot_flash_on_surface(self, surface):
        old_screen = self.screen
        self.screen = surface
        self.draw_shoot_flash()
        self.screen = old_screen

    def draw_debug_text_on_surface(self, surface):
        old_screen = self.screen
        self.screen = surface
        self.draw_debug_text()
        self.screen = old_screen

    def draw(self):
        if self.state == MENU:
            self.screen.fill(COLOR_BLACK)
            self.ui.draw_menu(self.screen, self.difficulty)

        elif self.state == PLAYING:
            self.screen.fill(COLOR_BLACK)
            self.draw_game_view()

        elif self.state == PAUSED:
            self.screen.fill(COLOR_BLACK)
            self.draw_game_view()
            self.ui.draw_pause_menu(self.screen)

        elif self.state == GAME_OVER:
            self.screen.fill(COLOR_BLACK)
            self.ui.draw_game_over(
                self.screen,
                self.score,
                self.kills,
                self.bosses_defeated,
                self.game_time,
                self.wave,
                self.high_scores,
                victory=False
            )

        elif self.state == WIN:
            self.screen.fill(COLOR_BLACK)
            self.ui.draw_game_over(
                self.screen,
                self.score,
                self.kills,
                self.bosses_defeated,
                self.game_time,
                self.wave,
                self.high_scores,
                victory=True
            )

        pygame.display.flip()

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle


if __name__ == "__main__":
    Game().run()
