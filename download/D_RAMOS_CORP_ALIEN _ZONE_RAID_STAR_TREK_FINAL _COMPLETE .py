#!/usr/bin/env python3
"""
D.RAMOS CORP ALIEN ZONE RAID - STAR TREK FINAL COMPLETE - 100% EVERYTHING - CEO 256-745254826
FINAL RELEASE - ENHANCED EDITION WITH MULTI-QUADRANT SHIELDS & LEADERS TELEMETRY

CEO 256-745254826 - POWERED BY D.RAMOS CORP ORG
Run: pip install pygame numpy
     python star_trek_game.py
"""
import pygame
import sys
import os
import time
import math
import random
import json
import numpy as np

CEO = "256-745254826"
POWERED_BY = "powered by D.RAMOS CORP ORG"
LEADERBOARD_FILE = "dramos_trek_telemetry.json"
WIDTH, HEIGHT = 1280, 720

# Corporate Color Palette Matrix
CYAN = (0, 255, 255)
GREEN = (50, 255, 80)
BLUE = (50, 120, 255)
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (255, 40, 40)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)

RANKS = [
    {"id": 0, "name": "Cadet 4th Class", "xp": 0, "color": (100, 100, 100), "ship": "Shuttle Type-15"},
    {"id": 1, "name": "Cadet 1st Class", "xp": 500, "color": (120, 120, 120), "ship": "Shuttle Type-6"},
    {"id": 2, "name": "Ensign", "xp": 1500, "color": (200, 150, 0), "ship": "Runabout Danube"},
    {"id": 3, "name": "Lieutenant JG", "xp": 3500, "color": (200, 150, 0), "ship": "Defiant"},
    {"id": 4, "name": "Lieutenant", "xp": 6500, "color": (200, 150, 0), "ship": "Nova"},
    {"id": 5, "name": "Lt Commander", "xp": 11000, "color": (180, 0, 0), "ship": "Intrepid Voyager"},
    {"id": 6, "name": "Commander", "xp": 17000, "color": (180, 0, 0), "ship": "Akira"},
    {"id": 7, "name": "Captain", "xp": 25000, "color": (180, 0, 0), "ship": "Constitution Enterprise"},
    {"id": 8, "name": "Commodore", "xp": 35000, "color": (200, 200, 200), "ship": "Excelsior"},
    {"id": 9, "name": "Rear Admiral", "xp": 50000, "color": (200, 200, 200), "ship": "Galaxy Enterprise-D"},
    {"id": 10, "name": "Vice Admiral", "xp": 70000, "color": (200, 200, 200), "ship": "Sovereign Enterprise-E"},
    {"id": 11, "name": "Admiral", "xp": 95000, "color": (200, 200, 200), "ship": "Odyssey"},
    {"id": 12, "name": "Fleet Admiral", "xp": 125000, "color": (255, 215, 0), "ship": "Yorktown Starbase 3M"},
]

ALL_MISSIONS_FINAL = [
    {"id": "MOV-01", "series": "MOVIE I 1979", "title": "V'Ger Cloud 82 AU", "planet": "V'Ger Earth Orbit", "civ": 2, "aliens": 4, "situation": "Save Ilia - AI consciousness V'Ger threatens Earth", "voice": "Kirk"},
    {"id": "MOV-02", "series": "MOVIE II 1982", "title": "Kobayashi Maru + Genesis + Khan", "planet": "Regula I + Kobayashi", "civ": 3, "aliens": 5, "situation": "No-win Kobayashi Maru - Save Genesis scientists Carol Marcus", "voice": "Khan"},
    {"id": "MOV-03", "series": "MOVIE III 1984", "title": "Search Spock Genesis Planet", "planet": "Genesis Unstable", "civ": 2, "aliens": 4, "situation": "Child Spock aging fast - Save Spock katra", "voice": "Spock"},
    {"id": "MOV-04", "series": "MOVIE IV 1986", "title": "Save Whales Time Travel 1986", "planet": "1986 San Francisco", "civ": 4, "aliens": 3, "situation": "Environmental whales extinct George Gracie", "voice": "Spock"},
    {"id": "TOS-01", "series": "TOS 1966", "title": "Arena Gorn Cestus III", "planet": "Cestus III Metron", "civ": 2, "aliens": 3, "situation": "Mercy Gorn captain Metron", "voice": "Kirk"},
]

pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    HAS_AUDIO = True
except Exception:
    HAS_AUDIO = False

def play_synth_sound(freq_start, freq_end, duration_ms, is_pulse=False):
    if not HAS_AUDIO: return
    sample_rate = 22050
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms / 1000.0, n_samples, endpoint=False)
    freqs = np.full(n_samples, freq_start) if freq_start == freq_end else np.linspace(freq_start, freq_end, n_samples)
    phases = 2 * np.pi * np.cumsum(freqs) / sample_rate
    signal = np.sin(phases)
    if is_pulse: signal = signal * (np.sin(2 * np.pi * 5 * t) > 0)
    signal = (signal * 16383).astype(np.int16)
    try:
        sound = pygame.mixer.Sound(buffer=signal)
        sound.play()
    except Exception: pass

def voice_synthesis(character):
    lines = {
        "Kirk": "Enterprise... phasers lock! Stand by transporter.",
        "Spock": "Fascinating... it is completely logical Captain.",
        "Picard": "Make it so! Engaging warp drive parameters now.",
        "Data": "Intriguing. My positronic matrix loops detect life.",
        "Khan": "From the heart of hell, I stab at thee!",
    }
    phrase = lines.get(character, "Alert status prioritized.")
    print(f"[{character} Executive Synth Voice]: {phrase}")
    play_synth_sound(130, 160, 500, is_pulse=True)

class StarTrekoZoneGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("D.RAMOS CORP ALIEN ZONE RAID - COGNITIVE LEADERBOARD MATRIX")
        self.clock = pygame.time.Clock()
        self.xp = 0
        self.rank_id = 0
        self.current_mission_index = 0
        self.running = True
        
        # Flight Parameters
        self.px, self.py = 200, 500
        self.p_vel_y = 0
        self.fuel = 100.0
        self.ship_active = False
        
        self.civilians = []
        self.aliens = []
        self.projectiles = []
        self.leaderboard = self.load_leaderboard()
        self.load_mission()

    def load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_to_leaderboard(self):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "xp": self.xp,
            "rank": RANKS[self.rank_id]["name"],
            "vessel": RANKS[self.rank_id]["ship"]
        }
        self.leaderboard.append(entry)
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x["xp"], reverse=True)[:5]
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
            print("[System Log]: Local telemetry scores updated on disk storage.")
        except Exception as e:
            print(f"File writing failure: {e}")

    def load_mission(self):
        self.mission = ALL_MISSIONS_FINAL[self.current_mission_index]
        self.civilians = []
        self.aliens = []
        self.projectiles = []
        
        for _ in range(self.mission["civ"]):
            self.civilians.append({
                "x": random.randint(200, WIDTH - 300),
                "y": random.randint(350, HEIGHT - 150),
                "saved": False
            })
            
        # Spawn targets with 4 distinct protective shield sectors
        for _ in range(self.mission["aliens"]):
            self.aliens.append({
                "x": random.randint(500, WIDTH - 150),
                "y": random.randint(180, HEIGHT - 250),
                "shields": {"fore": 100, "aft": 100, "dorsal": 100, "ventral": 100},
                "hull": 50
            })
        voice_synthesis(self.mission["voice"])
        play_synth_sound(440, 880, 250)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and self.fuel > 0:
            self.p_vel_y = -5.5
            self.fuel -= 0.5
            pygame.draw.circle(self.screen, ORANGE, (self.px + 15, self.py + 45), random.randint(6, 14))
        else:
            if self.fuel < 100.0: self.fuel += 0.15

        if keys[pygame.K_a]: self.px -= 6
        if keys[pygame.K_d]: self.px += 6
        if keys[pygame.K_w] and self.ship_active: self.py -= 6
        if keys[pygame.K_s] and self.ship_active: self.py += 6

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_to_leaderboard()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    play_synth_sound(800, 1200, 100)
                    self.projectiles.append({"x": self.px + 30, "y": self.py + 20, "dx": 14, "damage": 25})
                elif event.key == pygame.K_t:
                    self.beam_transporter_check()
                elif event.key == pygame.K_r:
                    self.current_mission_index = (self.current_mission_index + 1) % len(ALL_MISSIONS_FINAL)
                    self.load_mission()
                elif event.key == pygame.K_e:
                    self.ship_active = not self.ship_active

    def beam_transporter_check(self):
        for civ in self.civilians:
            if not civ["saved"] and abs(self.px - civ["x"]) < 90 and abs(self.py - civ["y"]) < 90:
                civ["saved"] = True
                self.xp += 200
                play_synth_sound(300, 1800, 600)
                self.check_rank_up()

    def check_rank_up(self):
        for rank in reversed(RANKS):
            if self.xp >= rank["xp"]:
                if rank["id"] > self.rank_id:
                    self.rank_id = rank["id"]
                    play_synth_sound(600, 1200, 500, is_pulse=True)
                break

    def update(self):
        if not self.ship_active:
            self.p_vel_y += 0.3
            self.py += self.p_vel_y
            if self.py >= HEIGHT - 130:
                self.py = HEIGHT - 130
                self.p_vel_y = 0

        for proj in self.projectiles[:]:
            proj["x"] += proj["dx"]
            if proj["x"] > WIDTH:
                self.projectiles.remove(proj)
                continue

            for al in self.aliens[:]:
                if abs(proj["x"] - al["x"]) < 45 and abs(proj["y"] - al["y"]) < 45:
                    if proj in self.projectiles: self.projectiles.remove(proj)
                    
                    # Impact resolution on Multi-Quadrant Shields (Fore Shield Absorbs Frontal Hits)
                    if al["shields"]["fore"] > 0:
Use code with caution.
al["shields"]["fore"] -= proj["damage"]
if al["shields"]["fore"] < 0: al["shields"]["fore"] = 0
play_synth_sound(150, 100, 150)
else:
al["hull"] -= proj["damage"]
if al["hull"] <= 0:
if al in self.aliens: self.aliens.remove(al)
self.xp += 150
self.check_rank_up()
break
def draw(self):
self.screen.fill(BLACK)
for i in range(25):
self.screen.set_at((random.randint(0, WIDTH), random.randint(0, HEIGHT)), WHITE)
for civ in self.civilians:
if not civ["saved"]:
pygame.draw.circle(self.screen, BLUE, (civ["x"], civ["y"]), 40, 2)
pygame.draw.circle(self.screen, CYAN, (civ["x"], civ["y"]), 8)
# Draw Targets with Visible Multi-Quadrant Protective Arcs
for al in self.aliens:
ax, ay = al["x"], al["y"]
pygame.draw.rect(self.screen, (40, 40, 50), (ax, ay, 40, 40))
# Fore Shield Arc Display
if al["shields"]["fore"] > 0:
pygame.draw.arc(self.screen, CYAN, (ax - 10, ay - 10, 60, 60), -math.pi/4, math.pi/4, 3)
# Dorsal Shield Arc Display
if al["shields"]["dorsal"] > 0:
pygame.draw.arc(self.screen, GREEN, (ax - 10, ay - 10, 60, 60), math.pi/4, 3*math.pi/4, 3)
# Hull Health Integrity Tracker
pygame.draw.rect(self.screen, RED, (ax, ay - 18, 40, 4))
pygame.draw.rect(self.screen, GREEN, (ax, ay - 18, int(40 * (al["hull"] / 50)), 4))
for proj in self.projectiles:
pygame.draw.line(self.screen, CYAN, (proj["x"], proj["y"]), (proj["x"] + 15, proj["y"]), 3)
if self.ship_active:
pygame.draw.ellipse(self.screen, CYAN, (self.px - 15, self.py - 5, 70, 35))
pygame.draw.rect(self.screen, WHITE, (self.px, self.py + 15, 40, 8))
else:
pygame.draw.rect(self.screen, GREEN, (self.px, self.py, 25, 45))
pygame.draw.circle(self.screen, YELLOW, (self.px + 12, self.py - 8), 8)
self.render_hud()
pygame.display.flip()
def render_hud(self):
font = pygame.font.SysFont("Consolas", 15)
# Upper Main Dashboard Panel
pygame.draw.rect(self.screen, (15, 15, 25), (10, 10, WIDTH - 20, 115))
pygame.draw.rect(self.screen, CYAN, (10, 10, WIDTH - 20, 115), 1)
rank_info = RANKS[self.rank_id]
hud_lines = [
(f"MISSION CODE CORE: {self.mission['title']} - {self.mission['series']}", CYAN),
(f"SITUATION PARAMS: {self.mission['situation']}", WHITE),
(f"OFFICER SECURITY HANDLE STATUS: {rank_info['name']} | CURRENT XP PROFILE SCORE: {self.xp}", GREEN),
(f"PILOT FUEL CORE MATRIX: {self.fuel:.1f}% | SECTOR DEFENSE MATRIX: FORE/DORSAL AUTOMATED ARCS ACTIVE", PURPLE),
(f"D.RAMOS CORP ENTERPRISE SYSTEM INFRASTRUCTURE MAIN MAP SECURITY NODE VERIFICATION: {CEO}", YELLOW)
]
for idx, (line, color) in enumerate(hud_lines):
self.screen.blit(font.render(line, True, color), (20, 15 + idx * 19))
# Right-aligned Telemetry Leaderboard Database Visual Container
pygame.draw.rect(self.screen, (20, 20, 30), (WIDTH - 310, 140, 290, 160))
pygame.draw.rect(self.screen, YELLOW, (WIDTH - 310, 140, 290, 160), 1)
self.screen.blit(font.render("🏆 DATABASE TELEMETRY BOARD", True, YELLOW), (WIDTH - 295, 145))
for idx, entry in enumerate(self.leaderboard):
lead_line = f"{idx+1}. {entry['xp']} XP - {entry['rank'][:12]}"
self.screen.blit(font.render(lead_line, True, WHITE), (WIDTH - 295, 170 + idx * 22))
def run(self):
while self.running:
self.handle_input()
self.update()
self.draw()
self.clock.tick(60)
pygame.quit()
sys.exit()
if name == "main":
StarTrekoZoneGame().run()