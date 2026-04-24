import sys
import os
import pygame
import math
import random
from collections import deque

# ═══════════════════════════════════════════════════════════════════
#  ASSET PATH HELPER
# ═══════════════════════════════════════════════════════════════════
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def asset(name):
    """Return full path for an asset file."""
    return os.path.join(ASSETS_DIR, name)


# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
SCREEN_W, SCREEN_H  = 950, 680
TILE                = 50
FPS                 = 60

DAMAGE_COOLDOWN     = 1000
SWORD_COOLDOWN      = 500
SWORD_SWING_DUR     = 260
SWORD_ARC           = math.pi * 0.9

CHEST_INTERACT_DIST = 65
COIN_COLLECT_DIST   = 22
COIN_FRICTION       = 0.82
COIN_GRAVITY        = 0.0
COIN_BOUNCE         = 0.38
COIN_STOP_SPEED     = 0.4

COLS = SCREEN_W // TILE   # 19
ROWS = SCREEN_H // TILE   # 13

# ── Colours ─────────────────────────────────────────────────────────
C_BG          = (18,  18,  28)
C_FLOOR       = (28,  28,  42)
C_FLOOR_BOSS  = (28,  10,  35)   # darker purple for boss room
C_WALL        = (52,  52,  78)
C_WALL_EDGE   = (72,  72, 105)
C_PLAYER      = (80,  200, 120)
C_MONSTER     = (200,  70,  70)
C_MONSTER_AGGRO = (140,  30,  30)
C_BULLET      = (255, 240,  80)
C_SHOTBULLET  = (255, 160,  40)
C_SWORD       = (180, 220, 255)
C_SWORD_SWING = (220, 255, 255)
C_CHEST       = (200, 160,  40)
C_CHEST_OPN   = ( 72,  48,  12)
C_COIN        = (255, 215,   0)
C_COIN_SHINE  = (255, 245, 160)
C_WHITE       = (240, 240, 240)
C_GREEN       = ( 80, 220, 120)
C_RED         = (220,  70,  70)
C_YELLOW      = (255, 240,  80)
C_ORANGE      = (255, 160,  40)
C_BLUE        = ( 80, 160, 255)
C_GREY        = (120, 120, 140)
C_DARK        = ( 10,  10,  20)
C_PANEL       = ( 26,  26,  42)
C_PANEL_EDGE  = ( 58,  58,  88)
C_SLOT_EMPTY  = ( 34,  34,  54)
C_SLOT_HOVER  = ( 50,  50,  80)
C_SLOT_ACTIVE = ( 60,  60, 100)
C_GATE_CLOSED = (180,  60,  30)
C_GATE_OPEN   = ( 60, 200, 255)
C_BOSS_HEALTH = (160,   0, 200)

# ── Level constants ──────────────────────────────────────────────────
BOSS_LEVEL          = 5     # which level spawns the boss
BASE_ENEMY_COUNT    = 3     # enemies on level 1
HP_SCALE_PER_LEVEL  = 0.18  # 18% HP increase per level
WIN_LEVEL           = BOSS_LEVEL  # clear boss level to win the run


# ═══════════════════════════════════════════════════════════════════
#  SPRITE LOADER  — loads all PNG assets; graceful fallback if missing
# ═══════════════════════════════════════════════════════════════════
class Sprites:
    """
    Central sprite cache.  Call Sprites.load() once after pygame.init().
    All images are stored as pygame.Surface objects with per-pixel alpha.
    Missing files are silently replaced with a None placeholder; rendering
    code checks for None and falls back to primitive shapes.
    """
    player        = None
    monster       = None
    monster_aggro = None
    boss          = None
    gate_closed   = None
    gate_open     = None
    guns: dict    = {}   # keyed by gun_type string
    sword_icon    = None

    @classmethod
    def load(cls):
        def _load(fname, size=None):
            path = asset(fname)
            if not os.path.exists(path):
                return None
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img

        cls.player        = _load("player.png",        (40, 40))
        cls.monster       = _load("monster.png",       (36, 36))
        cls.monster_aggro = _load("monster_aggro.png", (36, 36))
        cls.boss          = _load("boss.png",          (72, 72))
        cls.gate_closed   = _load("gate_closed.png",   (50, 50))
        cls.gate_open     = _load("gate_open.png",     (50, 50))
        cls.sword_icon    = _load("sword_icon.png")

        cls.guns = {
            "Pistol":        _load("pistol.png",        (32, 16)),
            "Shotgun":       _load("shotgun.png",       (40, 18)),
            "Assault Rifle": _load("assault_rifle.png", (44, 16)),
            "Revolver":      _load("revolver.png",      (36, 18)),
            "SMG":           _load("smg.png",           (36, 14)),
            "Sniper":        _load("sniper.png",        (48, 14)),
            "Machine Gun":   _load("machine_gun.png",   (48, 16)),
        }


def blit_rotated(surface, sprite, cx, cy, angle_rad):
    """
    Draw a sprite centred at (cx, cy) rotated by angle_rad.
    pygame.transform.rotate expects degrees and rotates CCW, so we negate.
    """
    if sprite is None:
        return
    deg = -math.degrees(angle_rad)
    rotated = pygame.transform.rotate(sprite, deg)
    rect    = rotated.get_rect(center=(int(cx), int(cy)))
    surface.blit(rotated, rect)


# ═══════════════════════════════════════════════════════════════════
#  TILE-GRID HELPERS
# ═══════════════════════════════════════════════════════════════════
def tile_rect(col, row):
    return pygame.Rect(col * TILE, row * TILE, TILE, TILE)

def world_to_tile(x, y):
    return x // TILE, y // TILE

def tile_center(col, row):
    return col * TILE + TILE // 2, row * TILE + TILE // 2

def norm(dx, dy):
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d else (0.0, 0.0)

def build_grid(walls):
    grid = [[True] * COLS for _ in range(ROWS)]
    for w in walls:
        c, r = world_to_tile(w.rect.x, w.rect.y)
        if 0 <= r < ROWS and 0 <= c < COLS:
            grid[r][c] = False
    return grid

def bfs_path(grid, start_tile, goal_tile):
    sc, sr = start_tile
    gc, gr = goal_tile
    if (sc, sr) == (gc, gr):
        return []
    visited = {(sc, sr)}
    queue   = deque()
    queue.append(((sc, sr), []))
    while queue:
        (cc, cr), path = queue.popleft()
        for dc, dr in ((1,0),(-1,0),(0,1),(0,-1)):
            nc, nr = cc + dc, cr + dr
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if (nc, nr) in visited:
                continue
            if not grid[nr][nc]:
                continue
            new_path = path + [(nc, nr)]
            if (nc, nr) == (gc, gr):
                return new_path
            visited.add((nc, nr))
            queue.append(((nc, nr), new_path))
    return []

def spawn_tile_away_from(avoid_tiles, min_tiles, grid, occupied_tiles=None):
    if occupied_tiles is None:
        occupied_tiles = set()
    attempts = 0
    while attempts < 500:
        c = random.randint(1, COLS - 2)
        r = random.randint(1, ROWS - 2)
        if not grid[r][c]:
            attempts += 1; continue
        if (c, r) in occupied_tiles:
            attempts += 1; continue
        too_close = any(
            max(abs(c - ac), abs(r - ar)) < min_tiles
            for (ac, ar) in avoid_tiles
        )
        if too_close:
            attempts += 1; continue
        return c, r
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            if grid[r][c] and (c, r) not in occupied_tiles:
                return c, r
    return 1, 1


# ═══════════════════════════════════════════════════════════════════
#  BASE ENTITY
# ═══════════════════════════════════════════════════════════════════
class GameEntity:
    def __init__(self, name, health, max_health, x, y, w=44, h=44):
        self.name       = name
        self.health     = health
        self.max_health = max_health
        self.rect       = pygame.Rect(x, y, w, h)
        self.speed      = 5
        self.facing     = 0.0  # angle in radians; 0 = right

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def draw_health_bar(self, surface, color=C_RED, offset_y=-10):
        bw    = self.rect.width
        ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(surface, (55, 0, 0),
                         (self.rect.x, self.rect.y + offset_y, bw, 5))
        pygame.draw.rect(surface, color,
                         (self.rect.x, self.rect.y + offset_y, int(bw * ratio), 5))


# ═══════════════════════════════════════════════════════════════════
#  WEAPONS
# ═══════════════════════════════════════════════════════════════════
class Weapon:
    def __init__(self, name, damage):
        self.name   = name
        self.damage = damage
    def weapon_color(self):
        return C_WHITE


class Sword(Weapon):
    LENGTH = 44
    WIDTH  = 7

    def __init__(self):
        super().__init__("Sword", 30)
        self._last_swing   = -SWORD_COOLDOWN
        self.base_angle    = 0.0
        self.current_angle = 0.0
        self.swinging      = False
        self._swing_start  = 0
        self._hit_set: set = set()

    def weapon_color(self):
        return C_SWORD

    @property
    def on_cooldown(self):
        return pygame.time.get_ticks() - self._last_swing < SWORD_COOLDOWN

    def swing(self, player_rect):
        if self.on_cooldown:
            return
        mx, my = pygame.mouse.get_pos()
        px, py = player_rect.center
        self.base_angle   = math.atan2(my - py, mx - px)
        self._last_swing  = pygame.time.get_ticks()
        self._swing_start = pygame.time.get_ticks()
        self.swinging     = True
        self._hit_set     = set()

    def update(self, player_rect):
        now = pygame.time.get_ticks()
        if self.swinging:
            elapsed = now - self._swing_start
            if elapsed >= SWORD_SWING_DUR:
                self.swinging      = False
                self.current_angle = self.base_angle + SWORD_ARC / 2
            else:
                t = elapsed / SWORD_SWING_DUR
                self.current_angle = (self.base_angle - SWORD_ARC / 2
                                      + SWORD_ARC * t)
        else:
            mx, my = pygame.mouse.get_pos()
            px, py = player_rect.center
            self.current_angle = math.atan2(my - py, mx - px)

    def check_hits(self, player_rect, monsters):
        if not self.swinging:
            return
        cx, cy    = player_rect.center
        arc_start = self.base_angle - SWORD_ARC / 2
        arc_end   = self.current_angle
        for i in range(14):
            t = i / 13
            a = arc_start + (arc_end - arc_start) * t
            for frac in (0.5, 0.75, 1.0, 1.1):
                reach = (14 + self.LENGTH) * frac
                pt = pygame.Rect(cx + math.cos(a) * reach - 7,
                                 cy + math.sin(a) * reach - 7, 14, 14)
                for m in monsters:
                    if m.health > 0 and id(m) not in self._hit_set:
                        if pt.colliderect(m.rect):
                            m.health -= self.damage
                            self._hit_set.add(id(m))

    def draw(self, surface, player_rect):
        cx, cy = player_rect.center
        a      = self.current_angle
        color  = C_SWORD_SWING if self.swinging else C_SWORD
        if self.swinging:
            arc_start = self.base_angle - SWORD_ARC / 2
            pts = [(int(cx + math.cos(arc_start + (a - arc_start) * t / 16) * (14 + self.LENGTH)),
                    int(cy + math.sin(arc_start + (a - arc_start) * t / 16) * (14 + self.LENGTH)))
                   for t in range(17)]
            if len(pts) >= 2:
                pygame.draw.lines(surface, (100, 180, 255), False, pts, 2)

        # Draw sword sprite if available, otherwise fallback lines
        if Sprites.sword_icon:
            blit_rotated(surface, Sprites.sword_icon,
                         cx + math.cos(a) * (14 + self.LENGTH // 2),
                         cy + math.sin(a) * (14 + self.LENGTH // 2),
                         a)
        else:
            bx = cx + math.cos(a) * 14;   by = cy + math.sin(a) * 14
            tx = cx + math.cos(a) * (14 + self.LENGTH)
            ty = cy + math.sin(a) * (14 + self.LENGTH)
            pygame.draw.line(surface, color, (int(bx), int(by)), (int(tx), int(ty)), self.WIDTH)
            hx = cx + math.cos(a + math.pi) * 7
            hy = cy + math.sin(a + math.pi) * 7
            pygame.draw.line(surface, (160, 120, 60), (int(cx), int(cy)), (int(hx), int(hy)), 5)


class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, color=C_BULLET, radius=5):
        self.x      = float(x)
        self.y      = float(y)
        self.dx     = dx * speed
        self.dy     = dy * speed
        self.damage = damage
        self.color  = color
        self.radius = radius
        self.alive  = True

    def update(self, w, h):
        self.x += self.dx
        self.y += self.dy
        if not (0 < self.x < w and 0 < self.y < h):
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Small bright core
        if self.radius > 3:
            pygame.draw.circle(surface, C_WHITE, (int(self.x), int(self.y)), max(1, self.radius - 2))


class Gun(Weapon):
    TYPES = {
        "Pistol":    dict(damage=20, speed=9,  fire_rate=400, spread=0,
                          bps=1, color=C_BULLET,    radius=5, barrel=24, mag_size=15, total_ammo=90),
        "Shotgun":   dict(damage=15, speed=7,  fire_rate=800, spread=0.35,
                          bps=4, color=C_SHOTBULLET, radius=4, barrel=28, mag_size=16, total_ammo=40),
        "Assault Rifle": dict(damage=10, speed=11, fire_rate=120, spread=0.08,
                          bps=1, color=C_BLUE,      radius=4, barrel=20, mag_size=30, total_ammo=150),
        "Revolver":  dict(damage=25, speed=8,  fire_rate=600, spread=0.02,
                          bps=1, color=(255, 200, 100), radius=5, barrel=22, mag_size=6, total_ammo=36),
        "SMG":       dict(damage=8,  speed=10, fire_rate=80,  spread=0.12,
                          bps=1, color=(150, 200, 255), radius=4, barrel=18, mag_size=25, total_ammo=200),
        "Sniper":    dict(damage=40, speed=14, fire_rate=1200, spread=0.01,
                          bps=1, color=(180, 100, 50), radius=6, barrel=32, mag_size=5, total_ammo=25),
        "Machine Gun": dict(damage=6, speed=9, fire_rate=50,  spread=0.15,
                          bps=1, color=(100, 100, 100), radius=4, barrel=26, mag_size=100, total_ammo=500),
    }

    def __init__(self, gun_type="Pistol", from_chest=False):
        cfg = self.TYPES[gun_type]
        super().__init__(gun_type, cfg["damage"])
        self.gun_type       = gun_type
        self.fire_rate      = cfg["fire_rate"]
        self.speed          = cfg["speed"]
        self.spread         = cfg["spread"]
        self.bps            = cfg["bps"]
        self.color          = cfg["color"]
        self.radius         = cfg["radius"]
        self.barrel         = cfg["barrel"]
        self._last_shot     = 0
        self.angle          = 0.0
        self.mag_size       = cfg["mag_size"]
        self.total_ammo     = cfg["total_ammo"]
        self.ammo_current   = cfg["mag_size"]
        self.ammo_reserve   = cfg["total_ammo"] - cfg["mag_size"]
        self.from_chest     = from_chest

    def weapon_color(self):
        return self.color

    @property
    def on_cooldown(self):
        return pygame.time.get_ticks() - self._last_shot < self.fire_rate

    def update_angle(self, player_rect):
        mx, my = pygame.mouse.get_pos()
        px, py = player_rect.center
        self.angle = math.atan2(my - py, mx - px)

    def fire(self, player_rect):
        if self.on_cooldown or self.ammo_current < self.bps:
            return []
        self._last_shot = pygame.time.get_ticks()
        self.ammo_current -= self.bps
        cx, cy = player_rect.center
        out = []
        for _ in range(self.bps):
            a = self.angle + random.uniform(-self.spread, self.spread)
            out.append(Bullet(cx, cy, math.cos(a), math.sin(a),
                              self.speed, self.damage, self.color, self.radius))
        return out

    def reload(self):
        if self.ammo_current == self.mag_size or self.ammo_reserve == 0:
            return
        ammo_needed  = self.mag_size - self.ammo_current
        ammo_to_take = min(ammo_needed, self.ammo_reserve)
        self.ammo_current   += ammo_to_take
        self.ammo_reserve   -= ammo_to_take

    def draw(self, surface, player_rect):
        """Draw gun sprite rotated toward mouse, or fallback primitives."""
        cx, cy  = player_rect.center
        sprite  = Sprites.guns.get(self.gun_type)

        if sprite:
            # Offset slightly ahead of the player centre
            offset = 14
            sx = cx + math.cos(self.angle) * offset
            sy = cy + math.sin(self.angle) * offset
            blit_rotated(surface, sprite, sx, sy, self.angle)
        else:
            # Fallback: plain line
            ex = cx + math.cos(self.angle) * self.barrel
            ey = cy + math.sin(self.angle) * self.barrel
            pygame.draw.line(surface, C_GREY, (int(cx), int(cy)), (int(ex), int(ey)), 6)
            pygame.draw.circle(surface, C_WHITE, (int(ex), int(ey)), 4)


# ═══════════════════════════════════════════════════════════════════
#  COIN
# ═══════════════════════════════════════════════════════════════════
class Coin:
    RADIUS = 6

    def __init__(self, x, y, vx=0.0, vy=0.0, value=1):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = vx
        self.vy    = vy
        self.value = value
        self.alive = True
        self._rest_timer = 0

    def update(self, walls):
        self.vx *= COIN_FRICTION
        self.vy *= COIN_FRICTION
        self.x  += self.vx
        coin_rect = pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)
        for w in walls:
            if coin_rect.colliderect(w.rect):
                if self.vx > 0:   self.x = w.rect.left  - self.RADIUS
                elif self.vx < 0: self.x = w.rect.right + self.RADIUS
                self.vx = -self.vx * COIN_BOUNCE
                if abs(self.vx) < COIN_STOP_SPEED: self.vx = 0
                coin_rect.x = self.x - self.RADIUS
        self.y += self.vy
        coin_rect.y = self.y - self.RADIUS
        for w in walls:
            if coin_rect.colliderect(w.rect):
                if self.vy > 0:   self.y = w.rect.top    - self.RADIUS
                elif self.vy < 0: self.y = w.rect.bottom + self.RADIUS
                self.vy = -self.vy * COIN_BOUNCE
                if abs(self.vy) < COIN_STOP_SPEED: self.vy = 0
                coin_rect.y = self.y - self.RADIUS
        if self.x - self.RADIUS < 0:
            self.x = self.RADIUS;     self.vx = -self.vx * COIN_BOUNCE
        elif self.x + self.RADIUS > SCREEN_W:
            self.x = SCREEN_W - self.RADIUS; self.vx = -self.vx * COIN_BOUNCE
        if self.y - self.RADIUS < 0:
            self.y = self.RADIUS;     self.vy = -self.vy * COIN_BOUNCE
        elif self.y + self.RADIUS > SCREEN_H:
            self.y = SCREEN_H - self.RADIUS; self.vy = -self.vy * COIN_BOUNCE
        if abs(self.vx) < COIN_STOP_SPEED and abs(self.vy) < COIN_STOP_SPEED:
            self._rest_timer += 1
        else:
            self._rest_timer = 0

    @property
    def at_rest(self):
        return self._rest_timer > 20

    def collect_rect(self):
        return pygame.Rect(self.x - COIN_COLLECT_DIST, self.y - COIN_COLLECT_DIST,
                           COIN_COLLECT_DIST * 2, COIN_COLLECT_DIST * 2)

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, C_COIN,       (ix, iy), self.RADIUS)
        pygame.draw.circle(surface, C_COIN_SHINE,  (ix - 2, iy - 2), 2)
        pygame.draw.circle(surface, (180, 140, 0), (ix, iy), self.RADIUS, 1)


def coin_burst(cx, cy, count=4, value=1):
    coins = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 4.5)
        coins.append(Coin(cx, cy,
                          vx=math.cos(angle) * speed,
                          vy=math.sin(angle) * speed,
                          value=value))
    return coins


# ═══════════════════════════════════════════════════════════════════
#  INVENTORY SLOT
# ═══════════════════════════════════════════════════════════════════
class InventorySlot:
    SIZE = 64

    def __init__(self, x, y, label=""):
        self.rect    = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.item    = None
        self.label   = label
        self.hovered = False

    def draw(self, surface, font_xs, font_sm, is_active=False):
        bg     = C_SLOT_ACTIVE if is_active else (C_SLOT_HOVER if self.hovered else C_SLOT_EMPTY)
        border = C_YELLOW if is_active else C_PANEL_EDGE
        pygame.draw.rect(surface, bg,     self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 1 + int(is_active), border_radius=6)
        if self.label:
            lt = font_xs.render(self.label, True, C_GREY)
            surface.blit(lt, (self.rect.x, self.rect.y - 16))
        if self.item is None:
            et = font_xs.render("empty", True, (70, 70, 95))
            surface.blit(et, (self.rect.x + self.SIZE // 2 - et.get_width() // 2,
                               self.rect.y + self.SIZE // 2 - et.get_height() // 2))
        else:
            col   = self.item.weapon_color()
            inner = self.rect.inflate(-12, -12)
            pygame.draw.rect(surface, col, inner, border_radius=4)
            nt = font_xs.render(self.item.name[:8], True, C_WHITE)
            surface.blit(nt, (self.rect.x + self.SIZE // 2 - nt.get_width() // 2,
                               self.rect.y + self.SIZE - 18))

    def contains(self, pos):
        return self.rect.collidepoint(pos)


# ═══════════════════════════════════════════════════════════════════
#  INVENTORY
# ═══════════════════════════════════════════════════════════════════
STORAGE_COLS = 5
STORAGE_ROWS = 4
STORAGE_SIZE = STORAGE_COLS * STORAGE_ROWS


class Inventory:
    SLOT_GAP  = 10
    PANEL_PAD = 18

    def __init__(self):
        self.open          = False
        self.equip_slots   = [InventorySlot(0, 0, "Weapon 1"),
                               InventorySlot(0, 0, "Weapon 2")]
        self.storage_slots = [InventorySlot(0, 0) for _ in range(STORAGE_SIZE)]
        self.active_equip  = 0
        self._drag_item    = None
        self._drag_src     = None
        self._drag_pos     = (0, 0)
        self._font_lg      = None
        self._font_sm      = None
        self._font_xs      = None
        self._layout_done  = False

    def init_fonts(self):
        self._font_lg = pygame.font.SysFont(None, 30)
        self._font_sm = pygame.font.SysFont(None, 22)
        self._font_xs = pygame.font.SysFont(None, 17)

    def _layout(self, sw, sh):
        if self._layout_done:
            return
        self._layout_done = True
        gap = self.SLOT_GAP
        ss  = InventorySlot.SIZE
        lx  = 60
        for i, slot in enumerate(self.equip_slots):
            slot.rect.x = lx + 20
            slot.rect.y = 120 + i * (ss + 40)
            slot.rect.w = ss
            slot.rect.h = ss
        rx   = sw // 2 + 20
        gx0  = rx + self.PANEL_PAD
        gy0  = 100
        for i, slot in enumerate(self.storage_slots):
            col = i % STORAGE_COLS
            row = i // STORAGE_COLS
            slot.rect.x = gx0 + col * (ss + gap)
            slot.rect.y = gy0 + row * (ss + gap)
            slot.rect.w = ss
            slot.rect.h = ss

    def has_weapon(self, weapon):
        if weapon is None:
            return False
        for slot in self.equip_slots + self.storage_slots:
            if slot.item is None:
                continue
            if isinstance(weapon, Gun) and isinstance(slot.item, Gun):
                if slot.item.gun_type == weapon.gun_type:
                    return True
            elif type(weapon) == type(slot.item):
                return True
        return False

    def add(self, weapon):
        if weapon is None:
            return False
        if self.has_weapon(weapon):
            return False
        for slot in self.equip_slots:
            if slot.item is None:
                slot.item = weapon
                return True
        for slot in self.storage_slots:
            if slot.item is None:
                slot.item = weapon
                return True
        return False

    @property
    def active_weapon(self):
        return self.equip_slots[self.active_equip].item

    def swap_equip(self):
        self.active_equip = 1 - self.active_equip

    def next_weapon(self):
        self.swap_equip()

    def prev_weapon(self):
        self.swap_equip()

    def toggle(self):
        self.open = not self.open
        self._layout_done = False

    def handle_mousedown(self, pos, sw, sh):
        self._layout(sw, sh)
        for i, slot in enumerate(self.equip_slots):
            if slot.contains(pos) and slot.item is not None:
                self._drag_item = slot.item
                self._drag_src  = ("equip", i)
                self._drag_pos  = pos
                slot.item       = None
                return
        for i, slot in enumerate(self.storage_slots):
            if slot.contains(pos) and slot.item is not None:
                self._drag_item = slot.item
                self._drag_src  = ("storage", i)
                self._drag_pos  = pos
                slot.item       = None
                return

    def handle_mousemotion(self, pos):
        self._drag_pos = pos

    def handle_mouseup(self, pos, sw, sh):
        self._layout(sw, sh)
        if self._drag_item is None:
            return
        dropped = False
        for i, slot in enumerate(self.equip_slots):
            if slot.contains(pos):
                old = slot.item
                slot.item       = self._drag_item
                self._drag_item = None
                if old is not None:
                    self._put_back(old)
                dropped = True
                break
        if not dropped:
            for i, slot in enumerate(self.storage_slots):
                if slot.contains(pos):
                    old = slot.item
                    slot.item       = self._drag_item
                    self._drag_item = None
                    if old is not None:
                        self._put_back(old)
                    dropped = True
                    break
        if not dropped:
            self._put_back(self._drag_item)
            self._drag_item = None

    def _put_back(self, item):
        if self._drag_src:
            kind, idx = self._drag_src
            slots = self.equip_slots if kind == "equip" else self.storage_slots
            if slots[idx].item is None:
                slots[idx].item = item
                self._drag_src  = None
                return
        for slot in self.storage_slots:
            if slot.item is None:
                slot.item = item
                return
        for slot in self.equip_slots:
            if slot.item is None:
                slot.item = item
                return

    def update_hover(self, pos, sw, sh):
        self._layout(sw, sh)
        for slot in self.equip_slots + self.storage_slots:
            slot.hovered = slot.contains(pos)

    def draw(self, surface):
        if self._font_lg is None:
            self.init_fonts()
        sw, sh = surface.get_size()
        self._layout(sw, sh)
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((6, 6, 16, 220))
        surface.blit(ov, (0, 0))
        title = self._font_lg.render("CHARACTER  (TAB to close)", True, C_WHITE)
        surface.blit(title, (sw // 2 - title.get_width() // 2, 14))
        lx, ly = 40, 55
        lw = sw // 2 - lx - 20
        lh = sh - 110
        _draw_panel(surface, lx, ly, lw, lh)
        eq_hdr = self._font_lg.render("EQUIPMENT", True, C_YELLOW)
        surface.blit(eq_hdr, (lx + lw // 2 - eq_hdr.get_width() // 2, ly + 12))
        for i, slot in enumerate(self.equip_slots):
            is_active = (i == self.active_equip)
            slot.draw(surface, self._font_xs, self._font_sm, is_active=is_active)
            if is_active:
                at = self._font_xs.render("ACTIVE", True, C_GREEN)
                surface.blit(at, (slot.rect.right + 8, slot.rect.centery - 6))
        aw = self.active_weapon
        if aw:
            sy       = self.equip_slots[-1].rect.bottom + 20
            stat_hdr = self._font_xs.render("   Active Weapon Stats", True, C_GREY)
            surface.blit(stat_hdr, (lx + 20, sy))
            if isinstance(aw, Gun):
                lines = [f"Type     : {aw.name}",
                         f"Damage   : {aw.damage}",
                         f"Speed    : {aw.speed}",
                         f"Fire Rate: {aw.fire_rate} ms",
                         f"Ammo     : {aw.ammo_current}/{aw.mag_size}",
                         f"Reserve  : {aw.ammo_reserve}"]
            elif isinstance(aw, Sword):
                lines = [f"Type     : Sword (melee)",
                         f"Damage   : {aw.damage}",
                         f"Style    : Arc sweep"]
            else:
                lines = []
            for j, line in enumerate(lines):
                lt = self._font_xs.render(line, True, C_WHITE)
                surface.blit(lt, (lx + 20, sy + 20 + j * 18))
        hints = ["Q  — swap weapon in game",
                 "Drag items between slots",
                 "TAB — close"]
        for i, h in enumerate(hints):
            ht = self._font_xs.render(h, True, C_GREY)
            surface.blit(ht, (lx + 14, ly + lh - 58 + i * 18))
        rx = sw // 2 + 20
        rw = sw - rx - 40
        rh = sh - 110
        _draw_panel(surface, rx, ly, rw, rh)
        st_hdr = self._font_lg.render("STORAGE", True, C_YELLOW)
        surface.blit(st_hdr, (rx + rw // 2 - st_hdr.get_width() // 2, ly + 12))
        used = sum(1 for s in self.storage_slots if s.item)
        cnt  = self._font_xs.render(f"{used}/{STORAGE_SIZE} slots used", True, C_GREY)
        surface.blit(cnt, (rx + rw - cnt.get_width() - 14, ly + 16))
        for slot in self.storage_slots:
            slot.draw(surface, self._font_xs, self._font_sm)
        if self._drag_item is not None:
            col   = self._drag_item.weapon_color()
            ghost = pygame.Surface((InventorySlot.SIZE, InventorySlot.SIZE), pygame.SRCALPHA)
            ghost.fill((*col, 120))
            surface.blit(ghost, (self._drag_pos[0] - InventorySlot.SIZE // 2,
                                  self._drag_pos[1] - InventorySlot.SIZE // 2))
            nt = self._font_xs.render(self._drag_item.name, True, C_WHITE)
            surface.blit(nt, (self._drag_pos[0] - nt.get_width() // 2,
                               self._drag_pos[1] + InventorySlot.SIZE // 2 + 2))

    def draw_hotbar(self, surface, font_sm):
        sw, sh = surface.get_size()
        ss     = 36
        gap    = 6
        total  = ss * 2 + gap
        bx     = sw // 2 - total // 2
        by     = sh - ss - 8
        for i, slot in enumerate(self.equip_slots):
            rx  = bx + i * (ss + gap)
            col = C_SLOT_ACTIVE if i == self.active_equip else C_SLOT_EMPTY
            pygame.draw.rect(surface, col,        (rx, by, ss, ss), border_radius=4)
            pygame.draw.rect(surface, C_PANEL_EDGE,(rx, by, ss, ss), 1, border_radius=4)
            if slot.item:
                wc = slot.item.weapon_color()
                pygame.draw.rect(surface, wc, (rx+4, by+4, ss-8, ss-8), border_radius=3)
            if i == self.active_equip:
                pygame.draw.rect(surface, C_YELLOW, (rx, by, ss, ss), 2, border_radius=4)
            num = font_sm.render(str(i+1), True, C_GREY)
            surface.blit(num, (rx + 2, by + 2))
        if self.active_weapon:
            nt = font_sm.render(self.active_weapon.name, True, C_YELLOW)
            surface.blit(nt, (sw // 2 - nt.get_width() // 2, by - 20))


def _draw_panel(surface, x, y, w, h):
    pygame.draw.rect(surface, C_PANEL,      (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, C_PANEL_EDGE, (x, y, w, h), 1, border_radius=10)


# ═══════════════════════════════════════════════════════════════════
#  WALL
# ═══════════════════════════════════════════════════════════════════
class Wall:
    def __init__(self, col, row):
        self.col  = col
        self.row  = row
        self.rect = tile_rect(col, row)

    def draw(self, surface):
        pygame.draw.rect(surface, C_WALL,      self.rect)
        pygame.draw.rect(surface, C_WALL_EDGE, self.rect, 2)


def build_maze():
    wall_set = set()
    for c in range(COLS):
        wall_set.add((c, 0));       wall_set.add((c, ROWS - 1))
    for r in range(1, ROWS - 1):
        wall_set.add((0, r));       wall_set.add((COLS - 1, r))
    interior = [
        (3,2),(4,2),(5,2),(3,3),(3,4),
        (12,2),(13,2),(14,2),(14,3),(14,4),(14,5),
        (9,2),(9,3),(9,5),(9,6),(9,7),(9,8),(9,9),(9,10),
        (2,8),(3,8),(4,8),(5,8),(2,9),(2,10),
        (13,9),(14,9),(15,9),(16,9),(16,8),(16,7),
        (11,5),(12,5),(13,5),
        (6,5),(7,5),(5,6),(5,7),
        (11,7),(12,7),(11,8),
    ]
    for (c, r) in interior:
        if 0 < c < COLS - 1 and 0 < r < ROWS - 1:
            wall_set.add((c, r))
    walls = [Wall(c, r) for (c, r) in wall_set]
    grid  = build_grid(walls)
    return walls, grid


def build_boss_maze():
    """
    Minimal maze for the boss arena — only border walls and
    four corner pillars to give a sense of space.
    """
    wall_set = set()
    for c in range(COLS):
        wall_set.add((c, 0));       wall_set.add((c, ROWS - 1))
    for r in range(1, ROWS - 1):
        wall_set.add((0, r));       wall_set.add((COLS - 1, r))
    # Corner pillars
    for (c, r) in [(3,3),(3,4),(4,3),(COLS-4,3),(COLS-4,4),(COLS-5,3),
                   (3,ROWS-4),(3,ROWS-5),(4,ROWS-4),(COLS-4,ROWS-4),(COLS-4,ROWS-5),(COLS-5,ROWS-4)]:
        if 0 < c < COLS-1 and 0 < r < ROWS-1:
            wall_set.add((c, r))
    walls = [Wall(c, r) for (c, r) in wall_set]
    grid  = build_grid(walls)
    return walls, grid


# ═══════════════════════════════════════════════════════════════════
#  CHEST
# ═══════════════════════════════════════════════════════════════════
class Chest:
    LOOT_TABLE = [
        lambda: Gun("Shotgun",       from_chest=True),
        lambda: Gun("Assault Rifle", from_chest=True),
        lambda: Gun("Revolver",      from_chest=True),
        lambda: Gun("SMG",           from_chest=True),
        lambda: Gun("Sniper",        from_chest=True),
        lambda: Gun("Pistol",        from_chest=True),
        lambda: Gun("Machine Gun",   from_chest=True),
    ]

    def __init__(self, col, row):
        self.col    = col
        self.row    = row
        self.rect   = tile_rect(col, row)
        self.opened = False
        self.loot   = random.choice(self.LOOT_TABLE)()

    def try_open(self, player_rect):
        if self.opened:
            return None, []
        dist = math.hypot(self.rect.centerx - player_rect.centerx,
                          self.rect.centery - player_rect.centery)
        if dist <= CHEST_INTERACT_DIST:
            self.opened = True
            coins = coin_burst(self.rect.centerx, self.rect.centery,
                               count=random.randint(3, 7), value=1)
            return self.loot, coins
        return None, []

    def draw(self, surface, font):
        if self.opened:
            pygame.draw.rect(surface, C_CHEST_OPN, self.rect, border_radius=6)
            pygame.draw.rect(surface, (100, 70, 20), self.rect, 2, border_radius=6)
            pygame.draw.line(surface, (130, 90, 25),
                             (self.rect.left + 4, self.rect.top + 8),
                             (self.rect.right - 4, self.rect.top + 8), 3)
            small_font = pygame.font.SysFont(None, 16)
            e  = small_font.render("empty", True, (90, 65, 25))
            surface.blit(e, (self.rect.centerx - e.get_width()//2,
                              self.rect.centery - e.get_height()//2))
        else:
            pygame.draw.rect(surface, C_CHEST, self.rect, border_radius=6)
            pygame.draw.rect(surface, (255, 210, 80), self.rect, 2, border_radius=6)
            cx, cy = self.rect.center
            pygame.draw.circle(surface, (40, 30, 10), (cx, cy - 2), 7)
            pygame.draw.rect(surface,   (40, 30, 10), (cx - 6, cy + 3, 12, 10))


# ═══════════════════════════════════════════════════════════════════
#  GATE  ─ appears when all enemies are defeated; transports player
#          to the next level when walked into.
# ═══════════════════════════════════════════════════════════════════
class Gate:
    """
    A tile-sized portal that starts LOCKED (red) until all enemies
    are dead.  Once OPEN (blue glow) touching it advances the level.
    """
    PULSE_SPEED = 3   # oscillations per second

    def __init__(self, col, row):
        self.col    = col
        self.row    = row
        self.rect   = tile_rect(col, row)
        self.locked = True   # True = waiting for enemies to die

    def unlock(self):
        self.locked = False

    def check_enter(self, player_rect):
        """Return True if the player is inside the open gate."""
        if self.locked:
            return False
        return self.rect.colliderect(player_rect)

    def draw(self, surface, font_xs):
        now = pygame.time.get_ticks() / 1000.0
        if self.locked:
            # Locked: dark red bars
            sprite = Sprites.gate_closed
            if sprite:
                surface.blit(sprite, self.rect.topleft)
            else:
                pygame.draw.rect(surface, C_GATE_CLOSED, self.rect, border_radius=4)
                pygame.draw.rect(surface, (240, 80, 40), self.rect, 2, border_radius=4)
            locked_txt = font_xs.render("LOCKED", True, (240, 80, 40))
            surface.blit(locked_txt, (self.rect.centerx - locked_txt.get_width()//2,
                                       self.rect.y - 16))
        else:
            # Open: pulsing cyan glow
            pulse = int(160 + 80 * math.sin(now * self.PULSE_SPEED * math.pi * 2))
            sprite = Sprites.gate_open
            if sprite:
                # Tint-flash the sprite by drawing a coloured overlay
                tinted = sprite.copy()
                tinted.fill((0, pulse // 4, pulse // 2, 0), special_flags=pygame.BLEND_RGBA_ADD)
                surface.blit(tinted, self.rect.topleft)
            else:
                pygame.draw.rect(surface, (20, pulse // 2, pulse), self.rect, border_radius=4)
                pygame.draw.rect(surface, C_GATE_OPEN, self.rect, 2, border_radius=4)
            # Glow rings
            for ring in range(3):
                alpha = max(0, 80 - ring * 25)
                rad   = 28 + ring * 6 + int(4 * math.sin(now * 4))
                ring_surf = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*C_GATE_OPEN, alpha), (rad, rad), rad, 2)
                surface.blit(ring_surf, (self.rect.centerx - rad, self.rect.centery - rad))
            enter_txt = font_xs.render("ENTER →", True, C_GATE_OPEN)
            surface.blit(enter_txt, (self.rect.centerx - enter_txt.get_width()//2,
                                      self.rect.y - 16))


# ═══════════════════════════════════════════════════════════════════
#  PLAYER
# ═══════════════════════════════════════════════════════════════════
class Player(GameEntity):
    def __init__(self, col, row):
        x, y = tile_center(col, row)
        super().__init__("Hero", 100, 100, x - 16, y - 16, w=40, h=40)
        self.speed          = 4
        self._last_hit_time = -DAMAGE_COOLDOWN
        self.invincible     = False
        self._inv_end       = 0
        self.money          = 0

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self._last_hit_time >= DAMAGE_COOLDOWN:
            self.health         -= amount
            self._last_hit_time  = now
            self.invincible      = True
            self._inv_end        = now + DAMAGE_COOLDOWN
            return True
        return False

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() > self._inv_end:
            self.invincible = False

    def move_with_walls(self, dx, dy, walls):
        self.rect.x += int(dx)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if dx > 0: self.rect.right  = w.rect.left
                else:       self.rect.left   = w.rect.right
        self.rect.y += int(dy)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if dy > 0: self.rect.bottom = w.rect.top
                else:       self.rect.top    = w.rect.bottom

    def draw(self, surface):
        flash = self.invincible and (pygame.time.get_ticks() // 100) % 2
        sprite = Sprites.player
        if sprite and not flash:
            # Rotate sprite to face mouse
            mx, my = pygame.mouse.get_pos()
            cx, cy = self.rect.center
            angle  = math.atan2(my - cy, mx - cx)
            # +pi/2 because sprite faces UP (angle=0 means right, so offset by 90°)
            blit_rotated(surface, sprite, cx, cy, angle + math.pi / 2)
        else:
            color = (255, 255, 255) if flash else C_PLAYER
            pygame.draw.rect(surface, color, self.rect, border_radius=6)
        self.draw_health_bar(surface, C_GREEN)


# ═══════════════════════════════════════════════════════════════════
#  MONSTER  — BFS pathfinding with aggro + sprite rendering
# ═══════════════════════════════════════════════════════════════════
class Monster(GameEntity):
    PATH_REFRESH_MS = 600
    AGGRO_RANGE     = 250

    def __init__(self, name, health, max_health, col, row):
        x, y = tile_center(col, row)
        super().__init__(name, health, max_health, x - 18, y - 18, w=36, h=36)
        self.speed          = 2.0
        self._path: list    = []
        self._path_timer    = 0
        self._coin_value    = random.randint(1, 3)
        self._speed_jitter  = random.uniform(0.85, 1.15)
        self.is_aggro       = False
        self._wander_dir    = [0.0, 0.0]
        self._wander_timer  = random.randint(60, 180)
        self._stuck_counter = 0

    def _my_tile(self):
        return world_to_tile(self.rect.centerx, self.rect.centery)

    def _check_aggro(self, player_rect):
        dist = math.hypot(player_rect.centerx - self.rect.centerx,
                          player_rect.centery - self.rect.centery)
        self.is_aggro = dist <= self.AGGRO_RANGE

    def update_path(self, player_rect, grid):
        now = pygame.time.get_ticks()
        if now - self._path_timer < self.PATH_REFRESH_MS:
            return
        self._path_timer = now
        goal = world_to_tile(player_rect.centerx, player_rect.centery)
        self._path = bfs_path(grid, self._my_tile(), goal)

    def _pick_wander_direction(self):
        self._wander_dir = [random.uniform(-1, 1), random.uniform(-1, 1)]
        n = math.hypot(self._wander_dir[0], self._wander_dir[1])
        if n > 0:
            self._wander_dir[0] /= n
            self._wander_dir[1] /= n
        self._wander_timer = random.randint(60, 180)

    def move_towards_player(self, player_rect, walls, grid):
        self._check_aggro(player_rect)
        move_x = move_y = 0.0
        if self.is_aggro:
            self.update_path(player_rect, grid)
            if self._path:
                nc, nr = self._path[0]
                tx, ty = tile_center(nc, nr)
                if math.hypot(tx - self.rect.centerx, ty - self.rect.centery) < 6:
                    self._path.pop(0)
            else:
                tx, ty = player_rect.centerx, player_rect.centery
            dx, dy = tx - self.rect.centerx, ty - self.rect.centery
            nx, ny = norm(dx, dy)
            spd    = self.speed * self._speed_jitter
            move_x = nx * spd
            move_y = ny * spd
            # Update facing for sprite rotation
            self.facing = math.atan2(dy, dx)
        else:
            self._wander_timer -= 1
            if self._wander_timer <= 0:
                self._pick_wander_direction()
            spd    = self.speed * 0.6
            move_x = self._wander_dir[0] * spd
            move_y = self._wander_dir[1] * spd
            if move_x or move_y:
                self.facing = math.atan2(move_y, move_x)

        self.rect.x += int(move_x)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_x > 0: self.rect.right  = w.rect.left
                else:           self.rect.left   = w.rect.right
        self.rect.y += int(move_y)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_y > 0: self.rect.bottom = w.rect.top
                else:           self.rect.top    = w.rect.bottom
        for w in walls:
            if self.rect.colliderect(w.rect):
                ol = self.rect.right  - w.rect.left
                or_ = w.rect.right   - self.rect.left
                ot = self.rect.bottom - w.rect.top
                ob = w.rect.bottom   - self.rect.top
                m  = min(ol, or_, ot, ob)
                if m == ol:   self.rect.right  = w.rect.left  - 1
                elif m == or_: self.rect.left  = w.rect.right + 1
                elif m == ot:  self.rect.bottom = w.rect.top  - 1
                else:          self.rect.top    = w.rect.bottom + 1

    def drop_coins(self):
        return coin_burst(self.rect.centerx, self.rect.centery,
                          count=self._coin_value + 1, value=1)

    def draw(self, surface):
        sprite = Sprites.monster_aggro if self.is_aggro else Sprites.monster
        if sprite:
            blit_rotated(surface, sprite,
                         self.rect.centerx, self.rect.centery,
                         self.facing + math.pi / 2)
        else:
            color = C_MONSTER_AGGRO if self.is_aggro else C_MONSTER
            pygame.draw.rect(surface, color, self.rect, border_radius=5)
            ex = self.rect.x + 10;  ey = self.rect.y + 12
            pygame.draw.circle(surface, C_YELLOW,   (ex,      ey), 4)
            pygame.draw.circle(surface, C_YELLOW,   (ex + 20, ey), 4)
            pygame.draw.circle(surface, (40, 0, 0), (ex +  1, ey), 2)
            pygame.draw.circle(surface, (40, 0, 0), (ex + 21, ey), 2)
        self.draw_health_bar(surface, C_RED)


# ═══════════════════════════════════════════════════════════════════
#  BOSS  — level 5 encounter; large, slow, deadly, sprite-rendered
# ═══════════════════════════════════════════════════════════════════
class Boss(GameEntity):
    """
    Boss entity for the final level.
    - Much higher HP, larger hitbox (72×72).
    - Slower base speed but bigger melee damage.
    - Uses BFS pathfinding like a monster.
    - Draws its own oversized health bar with purple colour.
    - Drops a big pile of coins on death.
    """
    PATH_REFRESH_MS = 400   # re-paths faster than normal monsters
    SIZE            = 72
    BASE_HP         = 500
    MELEE_DAMAGE    = 30    # damage per touch per second
    MELEE_RATE      = 1200  # ms between hits

    def __init__(self, col, row):
        x, y = tile_center(col, row)
        super().__init__("BOSS", self.BASE_HP, self.BASE_HP,
                         x - self.SIZE // 2, y - self.SIZE // 2,
                         w=self.SIZE, h=self.SIZE)
        self.speed          = 1.4
        self._path: list    = []
        self._path_timer    = 0
        self._last_hit_time = -self.MELEE_RATE
        # Pulse animation
        self._pulse         = 0.0

    def _my_tile(self):
        return world_to_tile(self.rect.centerx, self.rect.centery)

    def update_path(self, player_rect, grid):
        now = pygame.time.get_ticks()
        if now - self._path_timer < self.PATH_REFRESH_MS:
            return
        self._path_timer = now
        goal = world_to_tile(player_rect.centerx, player_rect.centery)
        self._path = bfs_path(grid, self._my_tile(), goal)

    def move_towards_player(self, player_rect, walls, grid):
        self.update_path(player_rect, grid)
        if self._path:
            nc, nr = self._path[0]
            tx, ty = tile_center(nc, nr)
            if math.hypot(tx - self.rect.centerx, ty - self.rect.centery) < 6:
                self._path.pop(0)
        else:
            tx, ty = player_rect.centerx, player_rect.centery
        dx, dy  = tx - self.rect.centerx, ty - self.rect.centery
        nx, ny  = norm(dx, dy)
        move_x  = nx * self.speed
        move_y  = ny * self.speed
        self.facing = math.atan2(dy, dx)

        self.rect.x += int(move_x)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_x > 0: self.rect.right  = w.rect.left
                else:           self.rect.left   = w.rect.right
        self.rect.y += int(move_y)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_y > 0: self.rect.bottom = w.rect.top
                else:           self.rect.top    = w.rect.bottom

    def try_hit_player(self, player):
        """Apply melee damage to player if touching; respects MELEE_RATE cooldown."""
        if not self.rect.colliderect(player.rect):
            return
        now = pygame.time.get_ticks()
        if now - self._last_hit_time >= self.MELEE_RATE:
            player.take_damage(self.MELEE_DAMAGE)
            self._last_hit_time = now

    def drop_coins(self):
        return coin_burst(self.rect.centerx, self.rect.centery,
                          count=20, value=3)

    def draw(self, surface):
        # Pulse effect
        self._pulse = (self._pulse + 0.05) % (math.pi * 2)
        sprite = Sprites.boss
        if sprite:
            scale  = 1.0 + 0.04 * math.sin(self._pulse)
            w      = int(self.SIZE * scale)
            scaled = pygame.transform.smoothscale(sprite, (w, w))
            blit_rotated(surface, scaled,
                         self.rect.centerx, self.rect.centery,
                         self.facing + math.pi / 2)
        else:
            # Fallback primitive
            pulse_r = int(5 * math.sin(self._pulse))
            color   = (max(0, 120 - pulse_r * 10), 0, min(255, 160 + pulse_r * 10))
            pygame.draw.ellipse(surface, color, self.rect.inflate(pulse_r, pulse_r))
            pygame.draw.ellipse(surface, (200, 0, 255),
                                self.rect.inflate(pulse_r, pulse_r), 3)

        # Full-width HP bar at the TOP of screen for boss fights
        bw     = SCREEN_W - 80
        bh     = 20
        bx, by = 40, 14
        ratio  = max(0.0, self.health / self.max_health)
        pygame.draw.rect(surface, (40, 0, 40),  (bx, by, bw, bh), border_radius=6)
        pygame.draw.rect(surface, C_BOSS_HEALTH,(bx, by, int(bw * ratio), bh), border_radius=6)
        pygame.draw.rect(surface, (200, 0, 255),(bx, by, bw, bh), 2, border_radius=6)

        font = pygame.font.SysFont(None, 18)
        label = font.render(f"BOSS  {max(0,self.health)}/{self.max_health}", True, (255,200,255))
        surface.blit(label, (bx + bw // 2 - label.get_width() // 2, by + 2))


# ═══════════════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════════════
def draw_hud(surface, player, chests, inventory, font_sm, font_xs, current_level):
    sw, sh = surface.get_size()
    pad    = 10

    # ── Health bar ──────────────────────────────────────────────────
    bar_w, bar_h = 180, 16
    bx, by = pad, pad + 20
    ratio  = max(0.0, player.health / player.max_health)
    pygame.draw.rect(surface, (55, 0, 0),  (bx, by, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, C_GREEN,     (bx, by, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(surface, C_WHITE,     (bx, by, bar_w, bar_h), 1, border_radius=4)
    hp = font_xs.render(f"HP  {max(0,player.health)}/{player.max_health}", True, C_WHITE)
    surface.blit(hp, (bx + 3, by + 1))
    hl = font_xs.render("HEALTH", True, C_GREY)
    surface.blit(hl, (bx, pad + 6))

    # ── Ammo counter ────────────────────────────────────────────────
    weapon = inventory.active_weapon
    if isinstance(weapon, Gun):
        ammo_y = by + bar_h + 6
        ammo_color = (C_RED if weapon.ammo_current == 0
                      else (C_YELLOW if weapon.ammo_current <= weapon.mag_size // 3
                            else C_WHITE))
        surface.blit(font_xs.render(f"MAG  {weapon.ammo_current}/{weapon.mag_size}", True, ammo_color),
                     (bx + 3, ammo_y))
        surface.blit(font_xs.render(f"Reserve: {weapon.ammo_reserve}", True,
                                    C_RED if weapon.ammo_reserve == 0 else C_GREY),
                     (bx + 3, ammo_y + 16))
        if weapon.ammo_current == 0 and weapon.ammo_reserve == 0:
            surface.blit(font_sm.render("OUT OF AMMO!", True, C_RED), (bx + 3, ammo_y + 32))

    # ── Money counter ───────────────────────────────────────────────
    mx = bx + bar_w + 16
    my = by + bar_h // 2
    pygame.draw.circle(surface, C_COIN,       (mx, my), 7)
    pygame.draw.circle(surface, C_COIN_SHINE,  (mx - 2, my - 2), 2)
    surface.blit(font_sm.render(f"{player.money}", True, C_YELLOW),
                 (mx + 14, my - font_sm.size("0")[1] // 2))

    # ── Level counter — top centre ───────────────────────────────────
    lv_txt = font_sm.render(f"Level  {current_level}  /  {WIN_LEVEL}", True, C_YELLOW)
    surface.blit(lv_txt, (sw // 2 - lv_txt.get_width() // 2, pad + 20))

    # Highlight boss level
    if current_level == BOSS_LEVEL:
        boss_warn = font_xs.render("⚠  BOSS LEVEL  ⚠", True, (255, 60, 255))
        surface.blit(boss_warn, (sw // 2 - boss_warn.get_width() // 2, pad + 38))

    # ── Chest prompt ────────────────────────────────────────────────
    for chest in chests:
        if not chest.opened:
            dist = math.hypot(chest.rect.centerx - player.rect.centerx,
                              chest.rect.centery - player.rect.centery)
            if dist <= CHEST_INTERACT_DIST:
                p = font_sm.render("[E] Open chest", True, C_YELLOW)
                surface.blit(p, (chest.rect.x - 6, chest.rect.y - 22))

    # ── Controls strip ──────────────────────────────────────────────
    ctrl = font_xs.render(
        "WASD move  |  Click/F attack  |  TAB inv  |  Q swap  |  E chest  |  R reload",
        True, C_GREY)
    surface.blit(ctrl, (sw // 2 - ctrl.get_width() // 2, 6))


def draw_end_screen(surface, won, font_lg, font_sm, current_level):
    sw, sh = surface.get_size()
    ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 165))
    surface.blit(ov, (0, 0))
    if won:
        lines = ["YOU WIN!", f"All {WIN_LEVEL} levels cleared!"]
        color = C_GREEN
    else:
        lines = ["GAME OVER", f"Reached level {current_level}"]
        color = C_RED
    t = font_lg.render(lines[0], True, color)
    s = font_sm.render(lines[1], True, C_WHITE)
    r = font_sm.render("R to restart  |  ESC quit", True, C_GREY)
    surface.blit(t, (sw // 2 - t.get_width() // 2, sh // 2 - 70))
    surface.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 - 20))
    surface.blit(r, (sw // 2 - r.get_width() // 2, sh // 2 + 20))


def draw_level_banner(surface, font_lg, current_level, alpha):
    """
    Flashes a 'LEVEL N' banner for a short time when entering a new level.
    alpha fades from 255 → 0.
    """
    sw, sh = surface.get_size()
    if current_level == BOSS_LEVEL:
        text  = "BOSS BATTLE!"
        color = (255, 80, 255)
    else:
        text  = f"Level  {current_level}"
        color = C_YELLOW
    surf = font_lg.render(text, True, color)
    surf.set_alpha(int(alpha))
    surface.blit(surf, (sw // 2 - surf.get_width() // 2, sh // 2 - 30))


# ═══════════════════════════════════════════════════════════════════
#  LEVEL FACTORY
# ═══════════════════════════════════════════════════════════════════
def make_level(grid, current_level, keep_player=None):
    """
    Spawn level entities.

    Parameters
    ----------
    grid         : walkable tile grid (built from the maze).
    current_level: int, 1-based current level number.
    keep_player  : existing Player to reuse (carries HP/money across levels).

    Returns
    -------
    player, monsters, boss, chests, gate
    """
    occupied = set()

    # ── Player ──────────────────────────────────────────────────────
    p_col, p_row = 1, 1
    occupied.add((p_col, p_row))
    if keep_player:
        player = keep_player
        px, py = tile_center(p_col, p_row)
        player.rect.x = px - player.rect.width  // 2
        player.rect.y = py - player.rect.height // 2
    else:
        player = Player(p_col, p_row)

    # ── Gate  — far corner ──────────────────────────────────────────
    g_col = COLS - 3
    g_row = ROWS - 3
    # Make sure gate tile is walkable
    while not grid[g_row][g_col] and g_col > 2:
        g_col -= 1
    occupied.add((g_col, g_row))
    gate = Gate(g_col, g_row)

    # ── Boss level ──────────────────────────────────────────────────
    if current_level == BOSS_LEVEL:
        bc, br = COLS // 2, ROWS // 2
        boss   = Boss(bc, br)
        occupied.add((bc, br))
        return player, [], boss, [], gate

    # ── Normal levels ────────────────────────────────────────────────
    boss          = None
    enemy_count   = BASE_ENEMY_COUNT + (current_level - 1)
    hp_scale      = 1.0 + HP_SCALE_PER_LEVEL * (current_level - 1)

    monsters = []
    for i in range(enemy_count):
        base_hp = int(random.choice([60, 80, 100]) * hp_scale)
        c, r    = spawn_tile_away_from([(p_col, p_row)], 5, grid, occupied)
        occupied.add((c, r))
        monsters.append(Monster(f"M{i}", base_hp, base_hp, c, r))

    # Chests (fewer on higher levels to increase difficulty)
    chest_count = max(1, 4 - (current_level - 1) // 2)
    chests      = []
    for _ in range(chest_count):
        c, r = spawn_tile_away_from([(p_col, p_row)], 3, grid, occupied)
        occupied.add((c, r))
        chests.append(Chest(c, r))

    return player, monsters, boss, chests, gate


def fresh_inventory():
    inv = Inventory()
    inv.init_fonts()
    inv.equip_slots[0].item = Sword()
    inv.equip_slots[1].item = Gun("Pistol", from_chest=False)
    return inv


# ═══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════
def run():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Dungeon Brawler")
    clock   = pygame.time.Clock()
    font_sm = pygame.font.SysFont(None, 22)
    font_lg = pygame.font.SysFont(None, 52)
    font_xs = pygame.font.SysFont(None, 17)

    # Load all sprite assets
    Sprites.load()

    # ── Build mazes (cached) ─────────────────────────────────────────
    normal_walls, normal_grid = build_maze()
    boss_walls,   boss_grid   = build_boss_maze()

    # ── Level banner animation state ─────────────────────────────────
    banner_alpha    = 0.0      # 0 = hidden
    BANNER_FADE_IN  = 60       # frames
    BANNER_HOLD     = 90       # frames
    BANNER_FADE_OUT = 60       # frames
    banner_timer    = 0        # frame counter within animation cycle

    def start_banner():
        nonlocal banner_alpha, banner_timer
        banner_alpha = 255.0
        banner_timer = 0

    # ── Full game reset ───────────────────────────────────────────────
    def reset():
        nonlocal current_level, banner_alpha, banner_timer
        current_level = 1
        inv           = fresh_inventory()
        walls, grid   = normal_walls, normal_grid
        pl, mo, bo, ch, ga = make_level(grid, current_level)
        start_banner()
        return inv, pl, mo, bo, ch, [], [], ga, walls, grid

    # ── Advance to next level (carries player + inventory) ───────────
    def next_level(inv, player):
        nonlocal current_level
        current_level += 1
        is_boss = (current_level == BOSS_LEVEL)
        walls   = boss_walls  if is_boss else normal_walls
        grid    = boss_grid   if is_boss else normal_grid
        pl, mo, bo, ch, ga = make_level(grid, current_level, keep_player=player)
        start_banner()
        return inv, pl, mo, bo, ch, [], [], ga, walls, grid

    current_level = 1
    inventory, player, monsters, boss, chests, bullets, coins, gate, walls, grid = reset()

    game_active = True
    game_over   = False
    you_win     = False

    running = True
    while running:
        clock.tick(FPS)

        # ── EVENTS ──────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                k = event.key

                if k == pygame.K_ESCAPE:
                    running = False

                elif k == pygame.K_TAB:
                    inventory.toggle()

                elif k == pygame.K_r and (game_over or you_win):
                    (inventory, player, monsters, boss,
                     chests, bullets, coins, gate, walls, grid) = reset()
                    game_active = True
                    game_over   = False
                    you_win     = False

                elif k == pygame.K_q and not inventory.open:
                    inventory.swap_equip()

                elif k == pygame.K_1:
                    inventory.active_equip = 0

                elif k == pygame.K_2:
                    inventory.active_equip = 1

                elif k == pygame.K_e and not inventory.open:
                    for chest in chests:
                        loot, burst = chest.try_open(player.rect)
                        if loot:
                            if isinstance(loot, Gun) and loot.from_chest:
                                merged = False
                                aw     = inventory.active_weapon
                                if isinstance(aw, Gun) and aw.gun_type == loot.gun_type:
                                    aw.ammo_reserve += loot.ammo_reserve + loot.ammo_current
                                    aw.reload()
                                    merged = True
                                else:
                                    for slot in inventory.equip_slots + inventory.storage_slots:
                                        if isinstance(slot.item, Gun) and slot.item.gun_type == loot.gun_type:
                                            slot.item.ammo_reserve += loot.ammo_reserve + loot.ammo_current
                                            slot.item.reload()
                                            merged = True
                                            break
                                if not merged:
                                    inventory.add(loot)
                            else:
                                inventory.add(loot)
                            coins.extend(burst)
                            break

                elif k == pygame.K_r and not inventory.open and game_active:
                    weapon = inventory.active_weapon
                    if isinstance(weapon, Gun):
                        weapon.reload()

                elif k == pygame.K_f and game_active and not inventory.open:
                    w = inventory.active_weapon
                    if isinstance(w, Sword):   w.swing(player.rect)
                    elif isinstance(w, Gun):   bullets.extend(w.fire(player.rect))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if inventory.open:
                    inventory.handle_mousedown(event.pos, SCREEN_W, SCREEN_H)
                elif game_active and event.button == 1:
                    w = inventory.active_weapon
                    if isinstance(w, Sword):   w.swing(player.rect)
                    elif isinstance(w, Gun):   bullets.extend(w.fire(player.rect))

            elif event.type == pygame.MOUSEMOTION:
                if inventory.open:
                    inventory.handle_mousemotion(event.pos)
                    inventory.update_hover(event.pos, SCREEN_W, SCREEN_H)

            elif event.type == pygame.MOUSEBUTTONUP:
                if inventory.open:
                    inventory.handle_mouseup(event.pos, SCREEN_W, SCREEN_H)

        # ── INVENTORY SCREEN ─────────────────────────────────────────
        if inventory.open:
            screen.fill(C_BG)
            for wall in walls: wall.draw(screen)
            inventory.draw(screen)
            pygame.display.flip()
            continue

        # ── END SCREEN ───────────────────────────────────────────────
        if not game_active:
            screen.fill(C_BG)
            for wall in walls: wall.draw(screen)
            for chest in chests: chest.draw(screen, font_sm)
            for m in monsters:
                if m.health > 0: m.draw(screen)
            if boss and boss.health > 0: boss.draw(screen)
            player.draw(screen)
            draw_end_screen(screen, you_win, font_lg, font_sm, current_level)
            pygame.display.flip()
            continue

        # ── PLAYER MOVEMENT ──────────────────────────────────────────
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += player.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= player.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += player.speed
        if dx and dy:
            dx /= math.sqrt(2); dy /= math.sqrt(2)
        player.move_with_walls(dx, dy, walls)
        player.rect.clamp_ip(pygame.Rect(TILE, TILE,
                                         SCREEN_W - TILE * 2, SCREEN_H - TILE * 2))
        player.update_invincibility()

        # ── WEAPON UPDATE ─────────────────────────────────────────────
        weapon = inventory.active_weapon
        if isinstance(weapon, Sword):  weapon.update(player.rect)
        elif isinstance(weapon, Gun):  weapon.update_angle(player.rect)

        # ── CONTINUOUS FIRE (held F) ──────────────────────────────────
        if keys[pygame.K_f] and game_active and not inventory.open:
            w = inventory.active_weapon
            if isinstance(w, Gun):   bullets.extend(w.fire(player.rect))
            elif isinstance(w, Sword): w.swing(player.rect)

        # ── BULLETS ───────────────────────────────────────────────────
        for b in bullets[:]:
            b.update(SCREEN_W, SCREEN_H)
            if not b.alive:
                bullets.remove(b); continue
            for wall in walls:
                if b.get_rect().colliderect(wall.rect):
                    b.alive = False
                    if b in bullets: bullets.remove(b)
                    break

        # ── MONSTER AI ───────────────────────────────────────────────
        for m in monsters:
            if m.health > 0:
                m.move_towards_player(player.rect, walls, grid)
                m.rect.clamp_ip(pygame.Rect(TILE, TILE,
                                            SCREEN_W - TILE*2, SCREEN_H - TILE*2))

        # ── BOSS AI ───────────────────────────────────────────────────
        if boss and boss.health > 0:
            boss.move_towards_player(player.rect, walls, grid)
            boss.rect.clamp_ip(pygame.Rect(TILE, TILE,
                                           SCREEN_W - TILE*2, SCREEN_H - TILE*2))
            boss.try_hit_player(player)

        # ── BULLET vs MONSTER ─────────────────────────────────────────
        for b in bullets[:]:
            if not b.alive: continue
            for m in monsters:
                if m.health > 0 and b.get_rect().colliderect(m.rect):
                    m.health -= b.damage
                    b.alive   = False
                    if b in bullets: bullets.remove(b)
                    if m.health <= 0:
                        coins.extend(m.drop_coins())
                    break
            # Boss hit by bullet
            if b.alive and boss and boss.health > 0:
                if b.get_rect().colliderect(boss.rect):
                    boss.health -= b.damage
                    b.alive = False
                    if b in bullets: bullets.remove(b)
                    if boss.health <= 0:
                        coins.extend(boss.drop_coins())

        # ── SWORD vs MONSTER / BOSS ──────────────────────────────────
        if isinstance(weapon, Sword):
            all_foes = monsters + ([boss] if boss and boss.health > 0 else [])
            prev_hp  = {id(f): f.health for f in all_foes}
            weapon.check_hits(player.rect, all_foes)
            for f in all_foes:
                if f.health <= 0 and prev_hp.get(id(f), 0) > 0:
                    coins.extend(f.drop_coins())

        # ── PLAYER vs MONSTER (contact) ───────────────────────────────
        for m in monsters:
            if m.health > 0 and player.rect.colliderect(m.rect):
                player.take_damage(15)

        # ── COIN PHYSICS & COLLECTION ─────────────────────────────────
        for coin in coins[:]:
            coin.update(walls)
            if coin.alive and player.rect.colliderect(coin.collect_rect()):
                player.money += coin.value
                coin.alive    = False
        coins = [c for c in coins if c.alive]

        # ── GATE LOGIC ───────────────────────────────────────────────
        # Enemies defeated → unlock gate
        all_enemies_dead = (
            all(m.health <= 0 for m in monsters) and
            (boss is None or boss.health <= 0)
        )
        if all_enemies_dead and gate.locked:
            gate.unlock()

        # Player enters open gate → advance level
        if gate.check_enter(player.rect):
            if current_level >= WIN_LEVEL:
                # Beat the boss level → game won
                game_active = False
                you_win     = True
            else:
                (inventory, player, monsters, boss,
                 chests, bullets, coins, gate, walls, grid) = next_level(inventory, player)

        # ── WIN / LOSE ────────────────────────────────────────────────
        if player.health <= 0:
            player.health = 0
            game_active   = False
            game_over     = True

        # ── DRAW ──────────────────────────────────────────────────────
        # Choose floor colour
        floor_color = C_FLOOR_BOSS if current_level == BOSS_LEVEL else C_FLOOR
        screen.fill(C_BG)

        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c]:
                    pygame.draw.rect(screen, floor_color,
                                     (c * TILE + 1, r * TILE + 1, TILE - 2, TILE - 2))

        for wall  in walls:    wall.draw(screen)
        gate.draw(screen, font_xs)
        for chest in chests:   chest.draw(screen, font_sm)
        for coin  in coins:    coin.draw(screen)
        for b     in bullets:  b.draw(screen)

        for m in monsters:
            if m.health > 0: m.draw(screen)

        if boss and boss.health > 0:
            boss.draw(screen)

        player.draw(screen)

        # Ammo under player
        if isinstance(weapon, Gun):
            ammo_str = f"mag {weapon.ammo_current}/{weapon.mag_size}"
            lbl = font_xs.render(ammo_str, True,
                                 C_YELLOW if weapon.ammo_current > 0 else C_RED)
            screen.blit(lbl, (player.rect.centerx - lbl.get_width() // 2,
                               player.rect.bottom + 4))

        if isinstance(weapon, Sword):    weapon.draw(screen, player.rect)
        elif isinstance(weapon, Gun):    weapon.draw(screen, player.rect)

        inventory.draw_hotbar(screen, font_sm)
        draw_hud(screen, player, chests, inventory, font_sm, font_xs, current_level)

        # ── Level banner ──────────────────────────────────────────────
        if banner_alpha > 0:
            draw_level_banner(screen, font_lg, current_level, banner_alpha)
            banner_timer += 1
            total = BANNER_FADE_IN + BANNER_HOLD + BANNER_FADE_OUT
            if banner_timer < BANNER_FADE_IN:
                banner_alpha = 255.0 * banner_timer / BANNER_FADE_IN
            elif banner_timer < BANNER_FADE_IN + BANNER_HOLD:
                banner_alpha = 255.0
            elif banner_timer < total:
                remaining    = total - banner_timer
                banner_alpha = 255.0 * remaining / BANNER_FADE_OUT
            else:
                banner_alpha = 0.0

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Game error:", e)
        import traceback; traceback.print_exc()
        pygame.quit()
        sys.exit(1)