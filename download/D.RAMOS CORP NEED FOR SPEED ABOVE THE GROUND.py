#!/usr/bin/env python3
"""
NEED FOR SPEED ABOVE THE GROUND - MULTIPLAYER ADVANCED COMBAT - UNIFIED PRODUCTION EDITION
- 6 Autonomous AI Vehicles Always Racing + 4 Optional Human Players (Up to 10 Planes Total).
- Offline Systems: Bouncing Plasma Cannons, Kinetic Particle Splashes, Dynamic Rain Vectors, 
  Neon Ground Reflections, and Hard-Drive Persistent JSON Telemetry Tracking.

CEO "256-745254826"
POWERED BY "powered by D.RAMOS CORP ORG"
Run: python nfs_above_ground_final.py
"""

import pygame
import random
import math
import sys
import os
import time
import json

CEO = "256-745254826"
APP_NAME = "NEED FOR SPEED ABOVE THE GROUND"
POWERED_BY = "powered by D.RAMOS CORP ORG"
LOGO_FILE = "dramos-logo.png"
DB_FILE = "nfs_telemetry_matrix.json"
WIDTH, HEIGHT = 1280, 720

# Corporate Structural Color Mapping Registry
CYAN = (0, 255, 255)
PURPLE = (138, 43, 226)
SILVER = (200, 200, 210)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 120, 255)
YELLOW = (255, 220, 0)
GREEN = (50, 255, 100)
ORANGE = (255, 140, 0)
PINK = (255, 50, 150)
BLACK = (5, 5, 8)

PLANE_COLORS = [
    {"name": "AUTO RED", "color": RED, "type": "auto"},
    {"name": "AUTO BLUE", "color": BLUE, "type": "auto"},
    {"name": "AUTO YELLOW", "color": YELLOW, "type": "auto"},
    {"name": "AUTO GREEN", "color": GREEN, "type": "auto"},
    {"name": "AUTO PURPLE", "color": PURPLE, "type": "auto"},
    {"name": "AUTO ORANGE", "color": ORANGE, "type": "auto"},
    {"name": "PLAYER 1 - WASD", "color": CYAN, "type": "player", "keys": {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "nos": pygame.K_SPACE, "fire": pygame.K_q}},
    {"name": "PLAYER 2 - ARROWS", "color": WHITE, "type": "player", "keys": {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "nos": pygame.K_RSHIFT, "fire": pygame.K_RCTRL}},
    {"name": "PLAYER 3 - IJKL", "color": PINK, "type": "player", "keys": {"up": pygame.K_i, "down": pygame.K_k, "left": pygame.K_j, "right": pygame.K_l, "nos": pygame.K_u, "fire": pygame.K_o}},
    {"name": "PLAYER 4 - TFGH", "color": SILVER, "type": "player", "keys": {"up": pygame.K_t, "down": pygame.K_g, "left": pygame.K_f, "right": pygame.K_h, "nos": pygame.K_y, "fire": pygame.K_r}},
]

def show_flash_and_select_players(duration_ms=4500):
    pygame.init()
    scr = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"{APP_NAME} MULTIPLAYER - Core Choice Matrix")
    clock = pygame.time.Clock()
    big = pygame.font.SysFont("monospace", 32, bold=True)
    med = pygame.font.SysFont("monospace", 20, bold=True)
    small = pygame.font.SysFont("monospace", 16)
    
    logo = None
    if os.path.exists(LOGO_FILE):
        try: logo = pygame.transform.scale(pygame.image.load(LOGO_FILE), (70, 70))
        except: pass
    
    selected_players = [True, True, False, False]
    start = time.time() * 1000
    flash_done = False
    
    while True:
        el = time.time() * 1000 - start
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: selected_players[0] = not selected_players[0]
                if e.key == pygame.K_2: selected_players[1] = not selected_players[1]
                if e.key == pygame.K_3: selected_players[2] = not selected_players[2]
                if e.key == pygame.K_4: selected_players[3] = not selected_players[3]
                if e.key in (pygame.K_SPACE, pygame.K_RETURN): flash_done = True
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
        
        if not flash_done and el < duration_ms:
            alpha = 255 if el < duration_ms - 1000 else int(255 * (1 - (el - (duration_ms - 1000)) / 1000))
        else:
            flash_done = True
            alpha = 255
        
        scr.fill(BLACK)
        pygame.draw.rect(scr, CYAN, (5, 5, WIDTH - 10, HEIGHT - 10), 2)
        
        if not flash_done:
            if logo: scr.blit(logo, (20, 20))
            t = big.render(APP_NAME + " EXTENDED", True, CYAN)
            t.set_alpha(alpha)
            scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 100))
            t2 = med.render("COMBAT ENGINE + WEATHER MATRIX + OFFLINE STORAGE LOGS", True, WHITE)
            t2.set_alpha(alpha)
            scr.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 150))
            
            prog = min(1.0, el / duration_ms)
            pygame.draw.rect(scr, (30, 30, 40), (340, 600, 600, 14))
            pygame.draw.rect(scr, CYAN, (340, 600, int(600 * prog), 14))
            scr.blit(small.render(POWERED_BY, True, (100, 180, 180)), (25, HEIGHT - 30))
        else:
            scr.blit(big.render("SELECT HUMAN VEHICLES - AI ALWAYS RACING", True, CYAN), (150, 30))
            y = 100
            for i in range(6):
                c = PLANE_COLORS[i]
                pygame.draw.rect(scr, c["color"], (60, y, 20, 20))
                scr.blit(small.render(f"{c['name']} - AUTO ACTIVE [COMPUTER LIFE]", True, WHITE), (90, y))
                y += 28
            
            y += 20
            for idx, sel in enumerate(selected_players):
                i = 6 + idx
                c = PLANE_COLORS[i]
                color = c["color"] if sel else (80, 80, 80)
                pygame.draw.rect(scr, color, (60, y, 20, 20))
                if sel: pygame.draw.rect(scr, WHITE, (60, y, 20, 20), 2)
                status = "ON - READY [PRESS CODE LINKED NUM TO TOGGLE]" if sel else "OFF - Press key [1-4] to hook allocation"
                scr.blit(small.render(f"{c['name']} - {status}", True, WHITE if sel else (120, 120, 120)), (90, y))
                y += 28
            
            y += 20
            scr.blit(med.render("Press SPACE or ENTER to initialize flight parameters...", True, GREEN), (150, y))
            
        pygame.display.flip()
        clock.tick(60)
        
        keys = pygame.key.get_pressed()
        if flash_done and (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]):
            time.sleep(0.3)
            return selected_players

class ParticleSplash:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 1)
        self.color = color
        self.life = random.randint(15, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25  
        self.life -= 1

class BouncingProjectile:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.owner = owner
        self.bounces = 0
        self.max_bounces = 3

    def update(self, buildings, engine):
        self.x += self.dx
        self.y += self.dy
        
        if self.y <= 0 or self.y >= HEIGHT:
            self.dy *= -1
            self.bounces += 1
            engine.create_impact_splash(self.x, self.y, RED)
            
        for b in buildings:
            if b["x"] < self.x < b["x"] + b["width"]:
                if abs(self.y - b["y"]) < 8:
                    self.dy *= -1
                    self.bounces += 1
                    engine.create_impact_splash(self.x, self.y, ORANGE)
                    break
                elif self.y > b["y"]:
                    self.dx *= -1
                    self.bounces += 1
                    engine.create_impact_splash(self.x, self.y, RED)
                    break

class PlaneMulti:
    def __init__(self, color_data, x, y):
        self.color_data = color_data
        self.name = color_data["name"]
        self.color = color_data["color"]
        self.type = color_data["type"]
        self.keys_map = color_data.get("keys", {})
        
        self.x = x
        self.y = y
        self.speed = random.uniform(8.0, 11.0)
        self.distance = 0.0
        self.nos_fuel = 100.0
        self.is_nos = False
        self.cooldown = 0

    def update(self, keys, buildings, engine):
        if self.cooldown > 0: self.cooldown -= 1

        if self.type == "player":
            if keys[self.keys_map["up"]] and self.y > 50: self.y -= 5
            if keys[self.keys_map["down"]] and self.y < HEIGHT - 50: self.y += 5
            if keys[self.keys_map["left"]] and self.x > 50: self.x -= 4
            if keys[self.keys_map["right"]] and self.x < WIDTH - 220: self.x += 4
            
            if keys[self.keys_map["nos"]] and self.nos_fuel > 0:
                self.is_nos = True
                self.nos_fuel -= 0.8
                self.speed = 15.5
            else:
                self.is_nos = False
                self.speed = 10.0
                if self.nos_fuel < 100.0: self.nos_fuel += 0.25
                
            if keys[self.keys_map["fire"]] and self.cooldown == 0:
                engine.projectiles.append(BouncingProjectile(self.x + 30, self.y, 14, random.choice([-2.5, 0, 2.5]), self))
                self.cooldown = 18
        else:
            self.is_nos = random.random() < 0.015 and self.nos_fuel > 30
            self.speed = 13.8 if self.is_nos else random.uniform(8.5, 11.5)
            if self.is_nos: self.nos_fuel -= 0.8
            elif self.nos_fuel < 100.0: self.nos_fuel += 0.2
            
            if random.random() < 0.01 and self.cooldown == 0:
                engine.projectiles.append(BouncingProjectile(self.x + 30, self.y, 12, random.choice([-2, 0, 2]), self))
                self.cooldown = 35

            for b in buildings:
                if b["x"] - self.x < 180 and b["x"] > self.x:
                    if self.y > b["y"] - 30: self.y -= 5

        self.distance += self.speed

    def draw(self, surf):
        if self.is_nos:
            pygame.draw.polygon(surf, ORANGE, [(self.x - 30, self.y), (self.x - 12, self.y - 5), (self.x - 12, self.y + 5)])
Use code with caution.
pygame.draw.polygon(surf, self.color, [(self.x + 25, self.y), (self.x - 15, self.y - 12), (self.x - 5, self.y), (self.x - 15, self.y + 12)])
pygame.draw.line(surf, WHITE, (self.x - 5, self.y - 18), (self.x - 5, self.y + 18), 2)
class CityRacingEngine:
def init(self, selected_players):
self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"{APP_NAME} - EXPERIMENTAL METRIC CORE")
self.clock = pygame.time.Clock()
self.running = True
self.buildings = []
self.planes = []
self.projectiles = []
self.particles = []
self.rain_drops = []
self.winner = None
self.database = self.load_database_logs()
self.generate_initial_scenery()
self.init_weather_matrix()
for i in range(6):
self.planes.append(PlaneMulti(PLANE_COLORS[i], 100, 80 + i * 65))
for idx, enabled in enumerate(selected_players):
if enabled:
self.planes.append(PlaneMulti(PLANE_COLORS[6 + idx], 120, 120 + idx * 75))
def load_database_logs(self):
if os.path.exists(DB_FILE):
try:
with open(DB_FILE, 'r') as f: return json.load(f)
except Exception: return []
return []
def commit_telemetry_logs(self):
if not self.winner: return
log_node = {
"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
"winner": self.winner,
"total_vehicles": len(self.planes),
"max_distance_track": 5000
}
self.database.append(log_node)
self.database = sorted(self.database, key=lambda x: x["timestamp"], reverse=True)[:5]
try:
with open(DB_FILE, 'w') as f: json.dump(self.database, f, indent=2)
print("[Database Log]: Telemetry metrics logged to offline disk memory node.")
except Exception as e: print(f"File writing block failure: {e}")
def generate_initial_scenery(self):
for i in range(12):
self.buildings.append({
"x": i * 160 + random.randint(0, 30),
"y": random.randint(380, 560),
"width": random.randint(90, 130),
"color": (12, 12, random.randint(28, 48))
})
def init_weather_matrix(self):
for _ in range(60):
self.rain_drops.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(7, 12)])
def create_impact_splash(self, x, y, color):
for _ in range(8):
self.particles.append(ParticleSplash(x, y, color))
def update(self):
for drop in self.rain_drops:
drop[1] += drop[2]
drop[0] -= 2
if drop[1] > HEIGHT:
drop[1] = 0
drop[0] = random.randint(0, WIDTH)
for b in self.buildings:
b["x"] -= 8
if b["x"] < -b["width"]:
b["x"] = WIDTH + random.randint(10, 50)
b["y"] = random.randint(380, 560)
for p in self.planes:
p.update(pygame.key.get_pressed(), self.buildings, self)
for b in self.buildings:
if b["x"] < p.x < b["x"] + b["width"] and p.y > b["y"]:
p.distance -= 120
p.x -= 20
self.create_impact_splash(p.x, p.y, YELLOW)
if p.distance >= 5000 and not self.winner:
self.winner = p.name
self.running = False
for proj in self.projectiles[:]:
proj.update(self.buildings, self)
if proj.bounces > proj.max_bounces or proj.x > WIDTH or proj.x < 0:
if proj in self.projectiles: self.projectiles.remove(proj)
continue
for target in self.planes:
if target != proj.owner and abs(proj.x - target.x) < 32 and abs(proj.y - target.y) < 22:
target.distance -= 200
self.create_impact_splash(target.x, target.y, RED)
if proj in self.projectiles: self.projectiles.remove(proj)
break
for part in self.particles[:]:
part.update()
if part.life <= 0: self.particles.remove(part)
def draw(self):
self.screen.fill(BLACK)
for drop in self.rain_drops:
pygame.draw.line(self.screen, (70, 90, 110), (drop[0], drop[1]), (drop[0] - 2, drop[1] + 8), 1)
for b in self.buildings:
pygame.draw.rect(self.screen, b["color"], (b["x"], b["y"], b["width"], HEIGHT - b["y"]))
pygame.draw.rect(self.screen, CYAN, (b["x"], b["y"], b["width"], HEIGHT - b["y"]), 1)
pygame.draw.rect(self.screen, (0, 40, 60), (b["x"], HEIGHT - 4, b["width"], 4))
for p in self.planes: p.draw(self.screen)
for proj in self.projectiles:
pygame.draw.circle(self.screen, RED, (int(proj.x), int(proj.y)), 6)
pygame.draw.circle(self.screen, YELLOW, (int(proj.x), int(proj.y)), 3)
for part in self.particles:
pygame.draw.circle(self.screen, part.color, (int(part.x), int(part.y)), random.randint(2, 4))
self.draw_dashboard_hud()
pygame.display.flip()
def draw_dashboard_hud(self):
font = pygame.font.SysFont("Consolas", 13)
pygame.draw.rect(self.screen, (10, 15, 30), (10, 10, 340, 240))
pygame.draw.rect(self.screen, CYAN, (10, 10, 340, 240), 1)
sorted_planes = sorted(self.planes, key=lambda p: p.distance, reverse=True)
for idx, p in enumerate(sorted_planes[:8]):
metrics = f"{idx+1}. {p.name[:14]} - {int(p.distance)}m | NOS: {int(p.nos_fuel)}%"
self.screen.blit(font.render(metrics, True, p.color), (20, 20 + idx * 26))
pygame.draw.rect(self.screen, (15, 15, 20), (WIDTH - 290, 10, 280, 140))
pygame.draw.rect(self.screen, YELLOW, (WIDTH - 290, 10, 280, 140), 1)
self.screen.blit(font.render("📊 OFFLINE HISTORIC METRICS", True, YELLOW), (WIDTH - 275, 18))
for idx, log in enumerate(self.database[:4]):
txt = f"{idx+1}. {log['winner'][:12]} - Match Finished"
self.screen.blit(font.render(txt, True, WHITE), (WIDTH - 275, 42 + idx * 22))
font_small = pygame.font.SysFont("Consolas", 11)
self.screen.blit(font_small.render(f"CEO SYSTEM OVERRIDE VERIFICATION IDENTIFIER: {CEO} | {POWERED_BY.upper()}", True, SILVER), (15, HEIGHT - 25))
def run(self):
while self.running:
for event in pygame.event.get():
if event.type == pygame.QUIT: self.running = False
self.update()
self.draw()
self.clock.tick(60)
self.commit_telemetry_logs()
if self.winner:
print(f"\n========================================\n🏁 COMPETITION CHAMPION: {self.winner}\n========================================")
pygame.quit()
if name == "main":
selected = show_flash_and_select_players()
if selected:
CityRacingEngine(selected).run()