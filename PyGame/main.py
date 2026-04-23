import sys
import pygame
import math
import random
from collections import deque

# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
# This section defines global game constants used throughout systems.
# - SCREEN_W, SCREEN_H: window size.
# - TILE: grid cell size; the map is tile-based.
# - FPS: game update rate.
# - DAMAGE_COOLDOWN: invulnerability time after player hit.
# - CHEST_INTERACT_DIST: how close the player must be to open a chest.
# - COIN_* constants: control coin physics behavior.  (COIN_GRAVITY is kept for introspection,
#   but coin behavior is now friction-only by default to prevent vertical dropping in top-down view.)
SCREEN_W, SCREEN_H  = 950, 680
TILE                = 50            
FPS                 = 60

DAMAGE_COOLDOWN     = 1000          # ms player invincibility after hit
SWORD_COOLDOWN      = 500           # ms between sword swings
SWORD_SWING_DUR     = 260           # ms the arc lasts
SWORD_ARC           = math.pi * 0.9

CHEST_INTERACT_DIST = 65            # px radius to open a chest
COIN_COLLECT_DIST   = 22            # px radius to auto-collect coin
COIN_FRICTION       = 0.82          # velocity damping each frame
COIN_GRAVITY        = 0.0           # zero gravity for top-down platformer
COIN_BOUNCE         = 0.38          # velocity retained on wall bounce
COIN_STOP_SPEED     = 0.4           # below this speed the coin rests

# Grid dimensions (in tiles)
COLS = SCREEN_W // TILE             # 19
ROWS = SCREEN_H // TILE             # 13

# ── Colours ─────────────────────────────────────────────────────────
C_BG          = (18,  18,  28)
C_FLOOR       = (28,  28,  42)
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


# ═══════════════════════════════════════════════════════════════════
#  TILE-GRID HELPERS
# ═══════════════════════════════════════════════════════════════════
def tile_rect(col, row): # Get Tile Rect
    """World rect of a tile at (col, row)."""
    return pygame.Rect(col * TILE, row * TILE, TILE, TILE)


def world_to_tile(x, y): # Convert the world to tiles
    """Pixel position → (col, row)."""
    return x // TILE, y // TILE


def tile_center(col, row): # Tile center position in pixels
    return col * TILE + TILE // 2, row * TILE + TILE // 2


def norm(dx, dy):  # Get hypotnuse 
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d else (0.0, 0.0)


def build_grid(walls): # Build a grid of walkable tiles based on wall positions
    """Return a 2-D bool array: grid[row][col] = True means WALKABLE."""
    grid = [[True] * COLS for _ in range(ROWS)]
    for w in walls:
        c, r = world_to_tile(w.rect.x, w.rect.y)
        if 0 <= r < ROWS and 0 <= c < COLS:
            grid[r][c] = False
    return grid


def bfs_path(grid, start_tile, goal_tile): # Breadth-first search for pathfinding on the tile grid, for monsters to get to the player
    """
    BFS from start_tile to goal_tile on the walkable grid.
    Returns a list of (col, row) tiles from start (exclusive) to goal,
    or [] if no path found.
    """
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
    return []          # no path


# ─── Tile-aligned spawn helper ──────────────────────────────────────
def spawn_tile_away_from(avoid_tiles, min_tiles, grid, occupied_tiles=None): # Create a spawn point for monsters that is a certain distance away from the player and other monsters, and not on a wall tile
    """
    Return a (col, row) of a walkable tile that is at least min_tiles
    distance from all avoid_tiles, and not in occupied_tiles.
    """
    if occupied_tiles is None:
        occupied_tiles = set()
    attempts = 0
    while attempts < 500:
        c = random.randint(1, COLS - 2)
        r = random.randint(1, ROWS - 2)
        if not grid[r][c]:
            attempts += 1
            continue
        if (c, r) in occupied_tiles:
            attempts += 1
            continue
        too_close = any(
            max(abs(c - ac), abs(r - ar)) < min_tiles
            for (ac, ar) in avoid_tiles
        )
        if too_close:
            attempts += 1
            continue
        return c, r
    # fallback: first open tile
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

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def draw_health_bar(self, surface, color=C_RED):
        bw    = self.rect.width
        ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(surface, (55, 0, 0),
                         (self.rect.x, self.rect.y - 8, bw, 5))
        pygame.draw.rect(surface, color,
                         (self.rect.x, self.rect.y - 8, int(bw * ratio), 5))


# ═══════════════════════════════════════════════════════════════════
#  WEAPONS
# ═══════════════════════════════════════════════════════════════════
# This section defines weapon classes and their logic.
#  - Weapon: base class for any equipable offensive item.
#  - Sword: melee weapon with swing arc and per-swing hit tracking.
#  - Gun: ranged weapon with bullet instantiation, spread, and cooldown.
#  - Bullet: moving projectile with straight flight and wall clipping.
# Implementation intent:
#   1) attach each weapon as player.active_weapon.
#   2) update() each frame for aiming/cooldown.
#   3) fire() returns projectiles to be simulated in the main loop.
#   4) draw() renders weapon UI and in-world effects.
# Changes: no logic changes here, just annotated for understanding.
class Weapon:
    def __init__(self, name, damage):
        self.name   = name
        self.damage = damage

    def weapon_color(self):
        """Return a representative colour for UI swatches."""
        return C_WHITE


# ── Sword ────────────────────────────────────────────────────────────
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
        """Sample points along the sweep arc; each monster hit once per swing."""
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
        bx = cx + math.cos(a) * 14;  by = cy + math.sin(a) * 14
        tx = cx + math.cos(a) * (14 + self.LENGTH)
        ty = cy + math.sin(a) * (14 + self.LENGTH)
        pygame.draw.line(surface, color, (int(bx), int(by)), (int(tx), int(ty)), self.WIDTH)
        hx = cx + math.cos(a + math.pi) * 7
        hy = cy + math.sin(a + math.pi) * 7
        pygame.draw.line(surface, (160, 120, 60), (int(cx), int(cy)), (int(hx), int(hy)), 5)


# ── Bullet ───────────────────────────────────────────────────────────
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


# ── Gun ──────────────────────────────────────────────────────────────
class Gun(Weapon):
    TYPES = {
        "Pistol":    dict(damage=20, speed=9,  fire_rate=400, spread=0,
                          bps=1, color=C_BULLET,    radius=5, barrel=24, mag_size=15, total_ammo=90),
        "Shotgun":   dict(damage=15, speed=7,  fire_rate=800, spread=0.35,
                          bps=5, color=C_SHOTBULLET, radius=4, barrel=28, mag_size=8, total_ammo=40),
        "Assault Rifle": dict(damage=10, speed=11, fire_rate=120, spread=0.08,
                          bps=1, color=C_BLUE,      radius=4, barrel=20, mag_size=30, total_ammo=150),
        "Revolver":  dict(damage=25, speed=8,  fire_rate=600, spread=0.02,
                          bps=1, color=(255, 200, 100), radius=5, barrel=22, mag_size=6, total_ammo=36),
        "SMG":       dict(damage=8,  speed=10, fire_rate=80,  spread=0.12,
                          bps=1, color=(150, 200, 255), radius=4, barrel=18, mag_size=25, total_ammo=200),
        "Sniper": dict(damage=40, speed=14, fire_rate=1200, spread=0.01,
                          bps=1, color=(180, 100, 50), radius=6, barrel=32, mag_size=5, total_ammo=25),
        "Machine Gun": dict(damage=6,  speed=9,  fire_rate=50,  spread=0.15,
                          bps=1, color=(100, 100, 100), radius=4, barrel=26, mag_size=100, total_ammo=500)
    }

    def __init__(self, gun_type="Pistol", from_chest=False):
        cfg = self.TYPES[gun_type]
        super().__init__(gun_type, cfg["damage"])
        self.gun_type   = gun_type
        self.fire_rate  = cfg["fire_rate"]
        self.speed      = cfg["speed"]
        self.spread     = cfg["spread"]
        self.bps        = cfg["bps"]
        self.color      = cfg["color"]
        self.radius     = cfg["radius"]
        self.barrel     = cfg["barrel"]
        self._last_shot = 0
        self.angle      = 0.0
        
        # Ammo system
        self.mag_size   = cfg["mag_size"]
        self.total_ammo = cfg["total_ammo"]
        self.ammo_current = cfg["mag_size"]  # Start with full magazine
        self.ammo_reserve = cfg["total_ammo"] - cfg["mag_size"]  # Remaining ammo in reserve
        
        # Track if from chest (non-droppable)
        self.from_chest = from_chest

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
        """Reload magazine from reserve ammo."""
        if self.ammo_current == self.mag_size or self.ammo_reserve == 0:
            return  # Already full or no ammo to reload
        ammo_needed = self.mag_size - self.ammo_current
        ammo_to_take = min(ammo_needed, self.ammo_reserve)
        self.ammo_current += ammo_to_take
        self.ammo_reserve -= ammo_to_take

    def draw(self, surface, player_rect):
        cx, cy = player_rect.center
        ex = cx + math.cos(self.angle) * self.barrel
        ey = cy + math.sin(self.angle) * self.barrel

        # Base gun barrel line
        width = 6
        if self.gun_type == "Shotgun":
            width = 10
        elif self.gun_type == "Sniper Rifle":
            width = 4
        elif self.gun_type == "SMG":
            width = 5
        elif self.gun_type == "Revolver":
            width = 7
        elif self.gun_type == "Machine Gun":
            width = 6

        pygame.draw.line(surface, C_GREY, (int(cx), int(cy)), (int(ex), int(ey)), width)

        # Weapon-specific muzzle or detail markers
        if self.gun_type == "Pistol":
            pygame.draw.rect(surface, self.color,
                             (int(ex), int(ey) - 3, 10, 6))
        elif self.gun_type == "Shotgun":
            for offset in (-3, 0, 3):
                sx = ex + math.cos(self.angle + offset * 0.09) * 12
                sy = ey + math.sin(self.angle + offset * 0.09) * 12
                pygame.draw.circle(surface, C_SHOTBULLET, (int(sx), int(sy)), 3)
        elif self.gun_type == "Assault Rifle":
            for i in range(3):
                bx = cx + math.cos(self.angle) * (self.barrel - 4 - i * 6)
                by = cy + math.sin(self.angle) * (self.barrel - 4 - i * 6)
                pygame.draw.circle(surface, (220, 220, 220), (int(bx), int(by)), 2)
        elif self.gun_type == "SMG":
            pygame.draw.circle(surface, C_BLUE, (int(cx), int(cy)), 4, 1)
        elif self.gun_type == "Revolver":
            pygame.draw.circle(surface, (180, 180, 180), (int(cx - 6), int(cy - 6)), 6, 2)
        elif self.gun_type == "Sniper Rifle":
            scope_x = cx + math.cos(self.angle) * (self.barrel * 0.5)
            scope_y = cy + math.sin(self.angle) * (self.barrel * 0.5)
            pygame.draw.circle(surface, (200, 200, 120), (int(scope_x), int(scope_y)), 4, 1)
        elif self.gun_type == "Machine Gun":
            scope_x = cx + math.cos(self.angle) * (self.barrel * 0.5)
            scope_y = cy + math.sin(self.angle) * (self.barrel * 0.5)
            pygame.draw.circle(surface, (200, 200, 120), (int(scope_x), int(scope_y)), 4, 1)

        pygame.draw.circle(surface, C_WHITE, (int(ex), int(ey)), 4)


# ═══════════════════════════════════════════════════════════════════
#  COIN  — physics drop from monster death / chest burst
# ═══════════════════════════════════════════════════════════════════
# Full behavior:
# 1) coin is spawned by coin_burst() with a random 2D velocity vector.
# 2) update() applies damping (COIN_FRICTION), moves in X/Y, and collides with walls.
# 3) no constant downwards gravity is applied for top-down context,
#    so coins behave as 2D scatterables rather than platform-fall objects.
# 4) when speed drops under COIN_STOP_SPEED, coin enters rest state.
# 5) collect_rect() is used to detect proximity pickup by player.

class Coin:
    RADIUS = 6

    def __init__(self, x, y, vx=0.0, vy=0.0, value=1):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = vx
        self.vy    = vy
        self.value = value
        self.alive = True
        self._rest_timer = 0    # frames coin has been nearly stopped

    def update(self, walls):
        # Apply friction to reduce velocity over time (2D top-down scatter).
        self.vx *= COIN_FRICTION
        self.vy *= COIN_FRICTION

        # Horizontal movement with wall collisions
        self.x += self.vx
        coin_rect = pygame.Rect(self.x - self.RADIUS,
                                self.y - self.RADIUS,
                                self.RADIUS * 2,
                                self.RADIUS * 2)
        for w in walls:
            if coin_rect.colliderect(w.rect):
                if self.vx > 0:
                    self.x = w.rect.left - self.RADIUS
                elif self.vx < 0:
                    self.x = w.rect.right + self.RADIUS
                self.vx = -self.vx * COIN_BOUNCE
                if abs(self.vx) < COIN_STOP_SPEED:
                    self.vx = 0
                coin_rect.x = self.x - self.RADIUS

        # Vertical movement with wall collisions
        self.y += self.vy
        coin_rect.y = self.y - self.RADIUS
        for w in walls:
            if coin_rect.colliderect(w.rect):
                if self.vy > 0:
                    self.y = w.rect.top - self.RADIUS
                elif self.vy < 0:
                    self.y = w.rect.bottom + self.RADIUS
                self.vy = -self.vy * COIN_BOUNCE
                if abs(self.vy) < COIN_STOP_SPEED:
                    self.vy = 0
                coin_rect.y = self.y - self.RADIUS

        # Boundaries to prevent coin escaping screen.
        if self.x - self.RADIUS < 0:
            self.x = self.RADIUS
            self.vx = -self.vx * COIN_BOUNCE
        elif self.x + self.RADIUS > SCREEN_W:
            self.x = SCREEN_W - self.RADIUS
            self.vx = -self.vx * COIN_BOUNCE

        if self.y - self.RADIUS < 0:
            self.y = self.RADIUS
            self.vy = -self.vy * COIN_BOUNCE
        elif self.y + self.RADIUS > SCREEN_H:
            self.y = SCREEN_H - self.RADIUS
            self.vy = -self.vy * COIN_BOUNCE

        if abs(self.vx) < COIN_STOP_SPEED and abs(self.vy) < COIN_STOP_SPEED:
            self._rest_timer += 1
        else:
            self._rest_timer = 0

    @property
    def at_rest(self):
        return self._rest_timer > 20

    def collect_rect(self):
        return pygame.Rect(self.x - COIN_COLLECT_DIST,
                           self.y - COIN_COLLECT_DIST,
                           COIN_COLLECT_DIST * 2, COIN_COLLECT_DIST * 2)

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, C_COIN,       (ix, iy), self.RADIUS)
        pygame.draw.circle(surface, C_COIN_SHINE,  (ix - 2, iy - 2), 2)
        pygame.draw.circle(surface, (180, 140, 0), (ix, iy), self.RADIUS, 1)


def coin_burst(cx, cy, count=4, value=1):
    """Return a list of Coin objects scattered from (cx, cy)."""
    coins = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 4.5)
        coins.append(Coin(cx, cy,
                          vx=math.cos(angle) * speed,
                          vy=math.sin(angle) * speed,   # 2D spread in top-down plane
                          value=value))
    return coins


# ═══════════════════════════════════════════════════════════════════
#  INVENTORY SLOT  — holds one Weapon or None
# ═══════════════════════════════════════════════════════════════════
# This section defines InventorySlot, a minimal UI container for a single item.
# 1) Each slot is fixed-size (SIZE x SIZE), storing either None or a weapon object.
# 2) 'contains(pos)' checks if mouse is inside the slot (used for drag/drop logic).
# 3) draw() renders the slot frame, active/hover state, and item icon/text.
# 4) This is low-level: InventorySlot does NOT manage movement itself; Inventory does.
#    InventorySlot is intentionally simple, while Inventory handles selection, swapping,
#    pick-up/dropback semantics, and full inventory layout.

class InventorySlot:
    """A single UI slot that can hold one item (weapon or None)."""
    SIZE = 64   # square side length in pixels

    def __init__(self, x, y, label=""):
        self.rect    = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.item    = None     # Weapon or None
        self.label   = label   # display label above slot
        self.hovered = False

    def draw(self, surface, font_xs, font_sm, is_active=False):
        # Background
        bg = C_SLOT_ACTIVE if is_active else (C_SLOT_HOVER if self.hovered else C_SLOT_EMPTY)
        pygame.draw.rect(surface, bg,         self.rect, border_radius=6)
        border = C_YELLOW if is_active else C_PANEL_EDGE
        pygame.draw.rect(surface, border,     self.rect, 1 + int(is_active), border_radius=6)

        # Label above
        if self.label:
            lt = font_xs.render(self.label, True, C_GREY)
            surface.blit(lt, (self.rect.x, self.rect.y - 16))

        if self.item is None:
            # Empty slot text
            et = font_xs.render("empty", True, (70, 70, 95))
            surface.blit(et, (self.rect.x + self.SIZE // 2 - et.get_width() // 2,
                               self.rect.y + self.SIZE // 2 - et.get_height() // 2))
        else:
            # Colour swatch block
            col = self.item.weapon_color()
            inner = self.rect.inflate(-12, -12)
            pygame.draw.rect(surface, col, inner, border_radius=4)
            # Short name
            nt = font_xs.render(self.item.name[:8], True, C_WHITE)
            surface.blit(nt, (self.rect.x + self.SIZE // 2 - nt.get_width() // 2,
                               self.rect.y + self.SIZE - 18))

    def contains(self, pos):
        return self.rect.collidepoint(pos)


# ═══════════════════════════════════════════════════════════════════
#  INVENTORY  — 2 equip slots (left) + 5×4 storage grid (right)
# ═══════════════════════════════════════════════════════════════════
# Inventory manages both equipment and storage:
# - equip_slots: 2 quick-access weapons; one active at a time (slot 0 or slot 1).
# - storage_slots: 5×4 = 20 long-term slots.
# - toggle() opens/closes the inventory (pausing gameplay in run loop).
# - _layout() computes exact screen positions on open and caches them for efficiency.
# - handle_mousedown / handle_mouseup / handle_mousemotion implement drag-and-drop:
#   * pickup item from slot
#   * store drag source kind/index
#   * drop into target or return to original slot
#   * swap if slot occupied
# - add() inserts a weapon into first free equip or storage slot,
#   making loot pickup immediate and automatic.
# - active_weapon is a property used by run() to resolve current weapon behaviour.
# - draw() renders darkened overlay, panels, equipped items and hover states.
# - draw_hotbar() renders bottom-center in-game quick access indicators.
# Additional internal fields:
#   _drag_item/_drag_src/_drag_pos: for mouse drag logic.
#   _layout_done: avoid recalculating layout every frame when inventory is open.

STORAGE_COLS = 5
STORAGE_ROWS = 4
STORAGE_SIZE = STORAGE_COLS * STORAGE_ROWS   # 20 slots


class Inventory:
    """
    Left panel  : 2 equipment slots (Weapon-1, Weapon-2).
    Right panel : 5×4 = 20 storage grid slots.
    Active weapon slot index: 0 or 1.  Press Q to swap in-game.
    Click to drag items between slots.
    """

    SLOT_GAP  = 10    # px gap between storage grid slots
    PANEL_PAD = 18

    def __init__(self):
        self.open          = False
        self.equip_slots   = [InventorySlot(0, 0, "Weapon 1"),
                               InventorySlot(0, 0, "Weapon 2")]
        self.storage_slots = [InventorySlot(0, 0) for _ in range(STORAGE_SIZE)]
        self.active_equip  = 0     # which equip slot is "in hand"
        self._drag_item    = None  # item being dragged
        self._drag_src     = None  # (kind, index)  kind = "equip"|"storage"
        self._drag_pos     = (0, 0)
        self._font_lg      = None
        self._font_sm      = None
        self._font_xs      = None
        # Layout is computed in draw() because we need surface size
        self._layout_done  = False

    def init_fonts(self):
        self._font_lg = pygame.font.SysFont(None, 30)
        self._font_sm = pygame.font.SysFont(None, 22)
        self._font_xs = pygame.font.SysFont(None, 17)

    # ── layout ───────────────────────────────────────────────────────
    def _layout(self, sw, sh):
        """Position all slots once per open."""
        if self._layout_done:
            return
        self._layout_done = True
        pad  = self.PANEL_PAD
        gap  = self.SLOT_GAP
        ss   = InventorySlot.SIZE

        # Left panel x-range: 40 … sw//2-20
        lx = 60
        # Equip slots stacked with gap
        for i, slot in enumerate(self.equip_slots):
            slot.rect.x = lx + 20
            slot.rect.y = 120 + i * (ss + 40)
            slot.rect.w = ss
            slot.rect.h = ss

        # Right panel x-range: sw//2+20 … sw-40
        rx = sw // 2 + 20
        grid_w = STORAGE_COLS * (ss + gap) - gap
        gx0 = rx + pad
        gy0 = 100
        for i, slot in enumerate(self.storage_slots):
            col = i % STORAGE_COLS
            row = i // STORAGE_COLS
            slot.rect.x = gx0 + col * (ss + gap)
            slot.rect.y = gy0 + row * (ss + gap)
            slot.rect.w = ss
            slot.rect.h = ss

    # ── adding items ─────────────────────────────────────────────────
    def has_weapon(self, weapon):
        """Check if equivalent weapon already exists in inventory."""
        if weapon is None:
            return False
        for slot in self.equip_slots + self.storage_slots:
            if slot.item is None:
                continue
            # For guns, match by type; for swords, by class.
            if isinstance(weapon, Gun) and isinstance(slot.item, Gun):
                if slot.item.gun_type == weapon.gun_type:
                    return True
            elif type(weapon) == type(slot.item):
                return True
        return False

    def add(self, weapon):
        """Put weapon in first empty storage slot (or equip slot if both free)."""
        if weapon is None:
            return False
        # prevent duplicates in equip/storage
        if self.has_weapon(weapon):
            return False

        # Fill equip slots first if empty
        for slot in self.equip_slots:
            if slot.item is None:
                slot.item = weapon
                return True
        # Else storage
        for slot in self.storage_slots:
            if slot.item is None:
                slot.item = weapon
                return True
        return False

    # ── active weapon ────────────────────────────────────────────────
    @property
    def active_weapon(self):
        return self.equip_slots[self.active_equip].item

    def swap_equip(self):
        """Toggle between equip slot 0 and 1."""
        self.active_equip = 1 - self.active_equip

    def next_weapon(self):
        self.swap_equip()

    def prev_weapon(self):
        self.swap_equip()

    def toggle(self):
        self.open = not self.open
        self._layout_done = False   # recompute layout on reopen

    # ── mouse interaction ────────────────────────────────────────────
    def handle_mousedown(self, pos, sw, sh):
        """Pick up item under cursor."""
        self._layout(sw, sh)
        # Check equip slots
        for i, slot in enumerate(self.equip_slots):
            if slot.contains(pos) and slot.item is not None:
                self._drag_item = slot.item
                self._drag_src  = ("equip", i)
                self._drag_pos  = pos
                slot.item       = None
                return
        # Check storage slots
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
        """Drop dragged item onto target slot."""
        self._layout(sw, sh)
        if self._drag_item is None:
            return
        dropped = False
        # Try equip slots
        for i, slot in enumerate(self.equip_slots):
            if slot.contains(pos):
                # Swap if occupied
                old = slot.item
                slot.item       = self._drag_item
                self._drag_item = None
                if old is not None:
                    self._put_back(old)
                dropped = True
                break
        if not dropped:
            # Try storage slots
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
            # Cannot drop chest weapons to storage
            if isinstance(self._drag_item, Gun) and self._drag_item.from_chest:
                self._put_back(self._drag_item)
            else:
                # Return item to source
                self._put_back(self._drag_item)
            self._drag_item = None

    def _put_back(self, item):
        """Return item to source slot or first free slot."""
        if self._drag_src:
            kind, idx = self._drag_src
            slots = self.equip_slots if kind == "equip" else self.storage_slots
            if slots[idx].item is None:
                slots[idx].item = item
                self._drag_src  = None
                return
        # Fall back: first free storage
        for slot in self.storage_slots:
            if slot.item is None:
                slot.item = item
                return
        # Last resort: first equip
        for slot in self.equip_slots:
            if slot.item is None:
                slot.item = item
                return

    def update_hover(self, pos, sw, sh):
        self._layout(sw, sh)
        for slot in self.equip_slots + self.storage_slots:
            slot.hovered = slot.contains(pos)

    # ── draw full overlay ────────────────────────────────────────────
    def draw(self, surface):
        if self._font_lg is None:
            self.init_fonts()
        sw, sh = surface.get_size()
        self._layout(sw, sh)

        # Dark overlay
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((6, 6, 16, 220))
        surface.blit(ov, (0, 0))

        # Title bar
        title = self._font_lg.render("CHARACTER  (TAB to close)", True, C_WHITE)
        surface.blit(title, (sw // 2 - title.get_width() // 2, 14))

        # ── LEFT panel ──────────────────────────────
        lx, ly = 40, 55
        lw = sw // 2 - lx - 20
        lh = sh - 110
        _draw_panel(surface, lx, ly, lw, lh)

        eq_hdr = self._font_lg.render("EQUIPMENT", True, C_YELLOW)
        surface.blit(eq_hdr, (lx + lw // 2 - eq_hdr.get_width() // 2, ly + 12))

        # Draw equip slots
        for i, slot in enumerate(self.equip_slots):
            is_active = (i == self.active_equip)
            slot.draw(surface, self._font_xs, self._font_sm, is_active=is_active)
            # "ACTIVE" tag
            if is_active:
                at = self._font_xs.render("ACTIVE", True, C_GREEN)
                surface.blit(at, (slot.rect.right + 8, slot.rect.centery - 6))

        # Stats of active weapon
        aw = self.active_weapon
        if aw:
            sy = self.equip_slots[-1].rect.bottom + 20
            stat_hdr = self._font_xs.render("   Active Weapon Stats", True, C_GREY)
            surface.blit(stat_hdr, (lx + 20, sy))
            if isinstance(aw, Gun):
                lines = [f"Type    : {aw.name}",
                         f"Damage  : {aw.damage}",
                         f"Speed   : {aw.speed}",
                         f"Fire Rate: {aw.fire_rate} ms",
                         f"Ammo    : {aw.ammo_current}/{aw.mag_size}",
                         f"Reserve : {aw.ammo_reserve}"]
                if aw.from_chest:
                    lines.append("Status  : [CHEST WEAPON]")
            elif isinstance(aw, Sword):
                lines = [f"Type    : Sword (melee)",
                         f"Damage  : {aw.damage}",
                         f"Style   : Arc sweep"]
            else:
                lines = []
            for j, line in enumerate(lines):
                lt = self._font_xs.render(line, True, C_WHITE)
                surface.blit(lt, (lx + 20, sy + 20 + j * 18))

        # Hint at bottom
        hints = ["Q  — swap weapon in game",
                 "Drag items between slots",
                 "TAB — close"]
        for i, h in enumerate(hints):
            ht = self._font_xs.render(h, True, C_GREY)
            surface.blit(ht, (lx + 14, ly + lh - 58 + i * 18))

        # ── RIGHT panel ─────────────────────────────
        rx = sw // 2 + 20
        rw = sw - rx - 40
        rh = sh - 110
        _draw_panel(surface, rx, ly, rw, rh)

        st_hdr = self._font_lg.render("STORAGE", True, C_YELLOW)
        surface.blit(st_hdr, (rx + rw // 2 - st_hdr.get_width() // 2, ly + 12))

        # Count
        used = sum(1 for s in self.storage_slots if s.item)
        cnt  = self._font_xs.render(f"{used}/{STORAGE_SIZE} slots used", True, C_GREY)
        surface.blit(cnt, (rx + rw - cnt.get_width() - 14, ly + 16))

        # Draw storage grid
        for slot in self.storage_slots:
            slot.draw(surface, self._font_xs, self._font_sm)

        # Drag ghost
        if self._drag_item is not None:
            col = self._drag_item.weapon_color()
            ghost = pygame.Surface((InventorySlot.SIZE, InventorySlot.SIZE),
                                   pygame.SRCALPHA)
            ghost.fill((*col, 120))
            surface.blit(ghost, (self._drag_pos[0] - InventorySlot.SIZE // 2,
                                  self._drag_pos[1] - InventorySlot.SIZE // 2))
            nt = self._font_xs.render(self._drag_item.name, True, C_WHITE)
            surface.blit(nt, (self._drag_pos[0] - nt.get_width() // 2,
                               self._drag_pos[1] + InventorySlot.SIZE // 2 + 2))

    # ── in-game hotbar ───────────────────────────────────────────────
    def draw_hotbar(self, surface, font_sm):
        sw, sh = surface.get_size()
        # Two small boxes bottom-centre
        ss    = 36
        gap   = 6
        total = ss * 2 + gap
        bx    = sw // 2 - total // 2
        by    = sh - ss - 8
        for i, slot in enumerate(self.equip_slots):
            rx = bx + i * (ss + gap)
            col = C_SLOT_ACTIVE if i == self.active_equip else C_SLOT_EMPTY
            pygame.draw.rect(surface, col,       (rx, by, ss, ss), border_radius=4)
            pygame.draw.rect(surface, C_PANEL_EDGE, (rx, by, ss, ss), 1, border_radius=4)
            if slot.item:
                wc = slot.item.weapon_color()
                pygame.draw.rect(surface, wc, (rx+4, by+4, ss-8, ss-8), border_radius=3)
            if i == self.active_equip:
                pygame.draw.rect(surface, C_YELLOW, (rx, by, ss, ss), 2, border_radius=4)
            num = font_sm.render(str(i+1), True, C_GREY)
            surface.blit(num, (rx + 2, by + 2))
        # Weapon name
        if self.active_weapon:
            nt = font_sm.render(self.active_weapon.name, True, C_YELLOW)
            surface.blit(nt, (sw // 2 - nt.get_width() // 2, by - 20))


def _draw_panel(surface, x, y, w, h):
    pygame.draw.rect(surface, C_PANEL,      (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, C_PANEL_EDGE, (x, y, w, h), 1, border_radius=10)


# ═══════════════════════════════════════════════════════════════════
#  WALL
# ═══════════════════════════════════════════════════════════════════
# Wall objects are static obstacles in the maze.
# - each wall is one tile in size, placed via tile_rect(col,row).
# - wall collision is used by player, monster, bullet, and coin update loops.
# - walls are built at maze creation time by build_maze() and converted to walkable grid.

class Wall:
    def __init__(self, col, row):
        self.col  = col
        self.row  = row
        self.rect = tile_rect(col, row)

    def draw(self, surface):
        pygame.draw.rect(surface, C_WALL,      self.rect)
        pygame.draw.rect(surface, C_WALL_EDGE, self.rect, 2)


def build_maze():
    """
    Build wall list from a tile-coordinate set.
    All walls are tile-aligned. Returns (walls, grid).
    """
    wall_set = set()

    # Border ring
    for c in range(COLS):
        wall_set.add((c, 0));         wall_set.add((c, ROWS - 1))
    for r in range(1, ROWS - 1):
        wall_set.add((0, r));         wall_set.add((COLS - 1, r))

    # Interior features
    interior = [
        # top-left room
        (3,2),(4,2),(5,2),(3,3),(3,4),
        # top-right cluster
        (12,2),(13,2),(14,2),(14,3),(14,4),(14,5),
        # centre vertical wall with gaps
        (9,2),(9,3),(9,5),(9,6),(9,7),(9,8),(9,9),(9,10),
        # bottom-left alcove
        (2,8),(3,8),(4,8),(5,8),(2,9),(2,10),
        # bottom-right corridor
        (13,9),(14,9),(15,9),(16,9),(16,8),(16,7),
        # mid horizontal barrier
        (11,5),(12,5),(13,5),
        # left side extra
        (6,5),(7,5),(5,6),(5,7),
        # mid-right pillars
        (11,7),(12,7),(11,8),
    ]
    for (c, r) in interior:
        if 0 < c < COLS - 1 and 0 < r < ROWS - 1:
            wall_set.add((c, r))

    walls = [Wall(c, r) for (c, r) in wall_set]
    grid  = build_grid(walls)
    return walls, grid


# ═══════════════════════════════════════════════════════════════════
#  CHEST
# ═══════════════════════════════════════════════════════════════════
# Chest objects are static tiles that can be opened by player proximity.
# - each chest has a random loot weapon and opened state flag.
# - try_open(player_rect) checks CHEST_INTERACT_DIST and mutates opened state.
# - when opened, returns (loot weapon, list of coins from coin_burst())
# - draw() renders closed/open chest graphics and "empty" text when opened.
# This is where item spawning and coin drops connect to player intent.

class Chest:
    LOOT_TABLE = [
        lambda: Gun("Shotgun", from_chest=True),
        lambda: Gun("Assault Rifle", from_chest=True),
        lambda: Gun("Revolver", from_chest=True),
        lambda: Gun("SMG", from_chest=True),
        lambda: Gun("Sniper", from_chest=True),
        lambda: Gun("Pistol", from_chest=True),
        lambda: Gun("Machine Gun", from_chest=True),
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
            # Burst coins out
            coins = coin_burst(self.rect.centerx, self.rect.centery,
                               count=random.randint(3, 7), value=1)
            return self.loot, coins
        return None, []

    def draw(self, surface, font):
        if self.opened:
            pygame.draw.rect(surface, C_CHEST_OPN, self.rect, border_radius=6)
            pygame.draw.rect(surface, (100, 70, 20), self.rect, 2, border_radius=6)
            pygame.draw.line(surface, (130, 90, 25),
                             (self.rect.left + 4,  self.rect.top + 8),
                             (self.rect.right - 4, self.rect.top + 8), 3)
            # center 'empty' label, smaller and visually consistent
            e_text = "empty"
            small_font = pygame.font.SysFont(None, 16)
            e = small_font.render(e_text, True, (90, 65, 25))
            ex = self.rect.centerx - e.get_width() // 2
            ey = self.rect.centery - e.get_height() // 2
            surface.blit(e, (ex, ey))
        else:
            pygame.draw.rect(surface, C_CHEST, self.rect, border_radius=6)
            pygame.draw.rect(surface, (255, 210, 80), self.rect, 2, border_radius=6)
            cx, cy = self.rect.center
            pygame.draw.circle(surface, (40, 30, 10), (cx, cy - 2), 7)
            pygame.draw.rect(surface,   (40, 30, 10), (cx - 6, cy + 3, 12, 10))


# ═══════════════════════════════════════════════════════════════════
#  PLAYER
# ═══════════════════════════════════════════════════════════════════
# Player entity represents the user-controlled hero.
# - inherits GameEntity for movement, health, and base rect.
# - manages invincibility frames and damage cooldown.
# - move_with_walls applies axis-separated collision to slide along walls.
# - draw() renders player block and forward health bar on top.
# - money field stores coins collected; updated in main loop via coin collisions.

class Player(GameEntity):
    def __init__(self, col, row):
        x, y = tile_center(col, row)
        super().__init__("Hero", 100, 100, x - 16, y - 16, w=40, h=40)
        self.speed          = 4
        self._last_hit_time = -DAMAGE_COOLDOWN
        self.invincible     = False
        self._inv_end       = 0
        self.money          = 0    # total coins collected

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
        """Axis-separated wall collision so player slides along surfaces."""
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
        color = (255, 255, 255) if flash else C_PLAYER
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        self.draw_health_bar(surface, C_GREEN)


# ═══════════════════════════════════════════════════════════════════
#  MONSTER  — BFS pathfinding with aggro system and NPC wandering
# ═══════════════════════════════════════════════════════════════════
# Monster AI now includes an aggro system:
# - monsters have an AGGRO_RANGE for detecting the player
# - when player is in range, monster becomes aggro'd and chases with BFS pathfinding
# - when not aggro'd, monsters wander randomly like NPCs
# - axis-separated collisions prevent wall-stuck behavior
# - monsters change to a darker red color when aggro'd
# - on death, monster drops coins via drop_coins() to be collected
# - draw() renders monster with color based on aggro state

class Monster(GameEntity):
    PATH_REFRESH_MS = 600   # recalculate path every N ms
    AGGRO_RANGE = 250       # pixels; detect player within this range

    def __init__(self, name, health, max_health, col, row):
        x, y = tile_center(col, row)
        super().__init__(name, health, max_health, x - 18, y - 18, w=36, h=36)
        self.speed           = 2.0
        self._path: list     = []      # list of (col, row) tiles to walk
        self._path_timer     = 0       # ms timestamp of last path update
        self._coin_value     = random.randint(1, 3)
        # Slight wobble per-monster so they don't stack perfectly
        self._speed_jitter   = random.uniform(0.85, 1.15)
        # Aggro system
        self.is_aggro        = False
        self._wander_dir     = [0.0, 0.0]  # current wander direction
        self._wander_timer   = random.randint(60, 180)  # frames until new wander direction
        self._stuck_counter  = 0  # counter for stuck detection

    def _my_tile(self):
        return world_to_tile(self.rect.centerx, self.rect.centery)

    def _check_aggro(self, player_rect):
        """Check if player is in aggro range."""
        dist = math.hypot(
            player_rect.centerx - self.rect.centerx,
            player_rect.centery - self.rect.centery
        )
        self.is_aggro = dist <= self.AGGRO_RANGE

    def update_path(self, player_rect, grid):
        """Refresh BFS path toward the player tile."""
        now = pygame.time.get_ticks()
        if now - self._path_timer < self.PATH_REFRESH_MS:
            return
        self._path_timer = now
        goal = world_to_tile(player_rect.centerx, player_rect.centery)
        self._path = bfs_path(grid, self._my_tile(), goal)

    def _pick_wander_direction(self):
        """Choose a new random direction for wandering."""
        self._wander_dir = [random.uniform(-1, 1), random.uniform(-1, 1)]
        n = math.hypot(self._wander_dir[0], self._wander_dir[1])
        if n > 0:
            self._wander_dir[0] /= n
            self._wander_dir[1] /= n
        self._wander_timer = random.randint(60, 180)

    def move_towards_player(self, player_rect, walls, grid):
        """
        If aggro'd: Follow BFS path to player and attack.
        If not aggro'd: Wander randomly like an NPC.
        Prevents sticking to walls with safe axis-separated collisions.
        """
        self._check_aggro(player_rect)

        move_x = 0.0
        move_y = 0.0

        if self.is_aggro:
            # Aggro mode: chase the player using BFS pathfinding
            self.update_path(player_rect, grid)

            # Determine target point
            if self._path:
                # Next waypoint is the centre of the next tile in path
                nc, nr = self._path[0]
                tx, ty = tile_center(nc, nr)
                # Pop waypoint when close enough
                if math.hypot(tx - self.rect.centerx, ty - self.rect.centery) < 6:
                    self._path.pop(0)
            else:
                # Same tile as player — direct chase
                tx, ty = player_rect.centerx, player_rect.centery

            dx, dy   = tx - self.rect.centerx, ty - self.rect.centery
            nx, ny   = norm(dx, dy)
            spd      = self.speed * self._speed_jitter
            move_x   = nx * spd
            move_y   = ny * spd
        else:
            # Not aggro'd: wander randomly like an NPC
            self._wander_timer -= 1
            if self._wander_timer <= 0:
                self._pick_wander_direction()

            spd = self.speed * 0.6  # slow wander speed
            move_x = self._wander_dir[0] * spd
            move_y = self._wander_dir[1] * spd

        # ─── SAFE AXIS-SEPARATED COLLISION ──────────────────────────
        # Move in X and resolve collisions
        self.rect.x += int(move_x)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_x > 0: 
                    self.rect.right  = w.rect.left
                else:           
                    self.rect.left   = w.rect.right

        # Move in Y and resolve collisions
        self.rect.y += int(move_y)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_y > 0: 
                    self.rect.bottom = w.rect.top
                else:           
                    self.rect.top    = w.rect.bottom
        
        # Final safety check: ensure we're not left inside any wall
        # If we are, nudge out gently
        for w in walls:
            if self.rect.colliderect(w.rect):
                # Push out in the direction with least overlap
                overlap_left   = self.rect.right - w.rect.left
                overlap_right  = w.rect.right - self.rect.left
                overlap_top    = self.rect.bottom - w.rect.top
                overlap_bottom = w.rect.bottom - self.rect.top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_left:
                    self.rect.right = w.rect.left - 1
                elif min_overlap == overlap_right:
                    self.rect.left = w.rect.right + 1
                elif min_overlap == overlap_top:
                    self.rect.bottom = w.rect.top - 1
                else:
                    self.rect.top = w.rect.bottom + 1

    def drop_coins(self):
        """Return coins scattered from the monster's death position."""
        return coin_burst(self.rect.centerx, self.rect.centery,
                          count=self._coin_value + 1, value=1)

    def draw(self, surface):
        # Change color based on aggro state
        color = C_MONSTER_AGGRO if self.is_aggro else C_MONSTER
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        ex = self.rect.x + 10;  ey = self.rect.y + 12
        pygame.draw.circle(surface, C_YELLOW,   (ex,      ey), 4)
        pygame.draw.circle(surface, C_YELLOW,   (ex + 20, ey), 4)
        pygame.draw.circle(surface, (40, 0, 0), (ex +  1, ey), 2)
        pygame.draw.circle(surface, (40, 0, 0), (ex + 21, ey), 2)
        self.draw_health_bar(surface, C_RED)


# ═══════════════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════════════
# This section renders the on-screen HUD overlay during active game play.
# draw_hud() is called each frame, draws:
#  - health bar and label (top-left)
#  - coin indicator/total (top-left, right of health)
#  - chest interaction prompt when near an unopened chest
#  - control hints (top-center)
# The function keeps HUD display decoupled from game state update logic.
# At runtime, coin and health values are read from player object.

def draw_hud(surface, player, chests, inventory, font_sm, font_xs):
    sw, sh = surface.get_size()
    pad    = 10

    # ── Health bar — TOP LEFT ────────────────────────────────────────
    bar_w, bar_h = 180, 16
    bx, by = pad, pad + 20
    ratio  = max(0.0, player.health / player.max_health)
    pygame.draw.rect(surface, (55, 0, 0),  (bx, by, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, C_GREEN,     (bx, by, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(surface, C_WHITE,     (bx, by, bar_w, bar_h), 1, border_radius=4)
    hp = font_xs.render(f"HP  {max(0,player.health)}/{player.max_health}", True, C_WHITE)
    surface.blit(hp, (bx + 3, by + 1))

    # ── HP label above bar ───────────────────────────────────────────
    hl = font_xs.render("HEALTH", True, C_GREY)
    surface.blit(hl, (bx, pad + 6))
    
    # ── Ammo counter — below health bar ──────────────────────────────
    weapon = inventory.active_weapon
    if isinstance(weapon, Gun):
        ammo_y = by + bar_h + 6
        ammo_color = C_RED if weapon.ammo_current == 0 else (C_YELLOW if weapon.ammo_current <= weapon.mag_size // 3 else C_WHITE)
        ammo_text = f"MAG  {weapon.ammo_current}/{weapon.mag_size}"
        ammo_display = font_xs.render(ammo_text, True, ammo_color)
        surface.blit(ammo_display, (bx + 3, ammo_y))
        
        # Reserve ammo info
        reserve_text = f"Reserve: {weapon.ammo_reserve}"
        reserve_color = C_RED if weapon.ammo_reserve == 0 else C_GREY
        reserve_display = font_xs.render(reserve_text, True, reserve_color)
        surface.blit(reserve_display, (bx + 3, ammo_y + 16))
        
        # Out of ammo warning
        if weapon.ammo_current == 0 and weapon.ammo_reserve == 0:
            out_msg = font_sm.render("OUT OF AMMO!", True, C_RED)
            surface.blit(out_msg, (bx + 3, ammo_y + 32))

    # ── Money counter — top-left, to the right of health bar ──────
    mx = bx + bar_w + 16
    my = by + bar_h // 2

    coin_icon_x = mx
    coin_icon_y = my

    pygame.draw.circle(surface, C_COIN, (coin_icon_x, coin_icon_y), 7)
    pygame.draw.circle(surface, C_COIN_SHINE, (coin_icon_x - 2, coin_icon_y - 2), 2)

    money_t = font_sm.render(f"{player.money}", True, C_YELLOW)
    surface.blit(money_t, (coin_icon_x + 14, coin_icon_y - money_t.get_height() // 2))

    # ── Chest prompt ─────────────────────────────────────────────────
    for chest in chests:
        if not chest.opened:
            dist = math.hypot(chest.rect.centerx - player.rect.centerx,
                              chest.rect.centery - player.rect.centery)
            if dist <= CHEST_INTERACT_DIST:
                p = font_sm.render("[E] Open chest", True, C_YELLOW)
                surface.blit(p, (chest.rect.x - 6, chest.rect.y - 22))

    # ── Controls strip — top centre ──────────────────────────────────
    ctrl = font_xs.render(
        "WASD move  |  Click/F attack  |  TAB inventory  |  Q swap weapon  |  E chest  |  R reload",
        True, C_GREY)
    surface.blit(ctrl, (sw // 2 - ctrl.get_width() // 2, 6))


def draw_end_screen(surface, won, font_lg, font_sm):
    sw, sh = surface.get_size()
    ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 165))
    surface.blit(ov, (0, 0))
    t = font_lg.render("YOU WIN!"  if won else "GAME OVER", True,
                        C_GREEN           if won else C_RED)
    s = font_sm.render("R to restart  |  ESC quit", True, C_WHITE)
    surface.blit(t, (sw // 2 - t.get_width() // 2, sh // 2 - 50))
    surface.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 + 14))


# ═══════════════════════════════════════════════════════════════════
#  LEVEL FACTORY
# ═══════════════════════════════════════════════════════════════════
# make_level() initializes a fresh game stage with:
#   * player at fixed start tile (1,1)
#   * monsters spawned at least 5 tiles away from the player
#   * chests spawned at least 3 tiles away while avoiding overlaps
# - uses spawn_tile_away_from() for valid walkable placement.
# - returns (player, monsters, chests) for run loop state.

# Helper fresh_inventory() seeds default weapons (Sword + Pistol).


def make_level(grid):
    """
    Spawn all entities at tile-aligned positions.
    Uses the walkable grid so nothing overlaps a wall.
    """
    occupied = set()

    # Player always at tile (1,1) — top-left open corner
    p_col, p_row = 1, 1
    occupied.add((p_col, p_row))
    player = Player(p_col, p_row)

    # Monsters — at least 5 tiles away from player
    monsters = []
    monster_hp = [60, 80, 100]
    for i, hp in enumerate(monster_hp):
        c, r = spawn_tile_away_from([(p_col, p_row)], 5, grid, occupied)
        occupied.add((c, r))
        monsters.append(Monster(f"M{i}", hp, hp, c, r))

    # Chests — tile-aligned, not overlapping walls or each other
    chests = []
    for _ in range(4):
        c, r = spawn_tile_away_from([(p_col, p_row)], 3, grid, occupied)
        occupied.add((c, r))
        chests.append(Chest(c, r))

    return player, monsters, chests


def fresh_inventory():
    """Starting loadout: Sword in slot-0, Pistol in slot-1."""
    inv = Inventory()
    inv.init_fonts()
    inv.equip_slots[0].item = Sword()
    inv.equip_slots[1].item = Gun("Pistol", from_chest=False)
    return inv


# ═══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════
# run() is the backbone of the game: one frame per iteration, all systems integrated.
# Sequence:
# 1) event processing (keyboard/mouse)
# 2) inventory state check (pauses the game world)
# 3) player movement and wall collision
# 4) active weapon updates (sword swing or gun aim)
# 5) bullets updates and collision handling
# 6) monster pathfinding + movement + combat checks
# 7) player damage and coin collection logic
# 8) win/lose conditions
# 9) render world in correct draw order (floor->walls->entities->HUD)
#
# This function keeps all global game states (player, enemies, bullets, coins, chests, inventory)
# and runs them together until quit.

def run():
    pygame.init()
    screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Dungeon Brawler")
    clock    = pygame.time.Clock()
    font_sm  = pygame.font.SysFont(None, 22)
    font_lg  = pygame.font.SysFont(None, 42)
    font_xs  = pygame.font.SysFont(None, 17)

    # Build map once; grid is reused every level
    walls, grid = build_maze()

    def reset():
        inv  = fresh_inventory()
        pl, mo, ch = make_level(grid)
        return inv, pl, mo, ch, [], []   # inv, player, monsters, chests, bullets, coins

    inventory, player, monsters, chests, bullets, coins = reset()
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
                    inventory, player, monsters, chests, bullets, coins = reset()
                    game_active = True;  game_over = False;  you_win = False

                elif k == pygame.K_q and not inventory.open:
                    inventory.swap_equip()    # swap active weapon slot
                
                elif k == pygame.K_1:
                    inventory.active_equip = 0

                elif k == pygame.K_2:
                    inventory.active_equip = 1

                elif k == pygame.K_e and not inventory.open:
                    for chest in chests:
                        loot, burst = chest.try_open(player.rect)
                        if loot:
                            if isinstance(loot, Gun) and loot.from_chest:
                                # Merge ammo into existing same-type gun
                                merged = False
                                active_weapon = inventory.active_weapon
                                if isinstance(active_weapon, Gun) and active_weapon.gun_type == loot.gun_type:
                                    active_weapon.ammo_reserve += loot.ammo_reserve + loot.ammo_current
                                    active_weapon.reload()
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
                    # Reload current weapon if it's a gun
                    weapon = inventory.active_weapon
                    if isinstance(weapon, Gun):
                        weapon.reload()

                elif k == pygame.K_f and game_active and not inventory.open:
                    w = inventory.active_weapon
                    if isinstance(w, Sword):  w.swing(player.rect)
                    elif isinstance(w, Gun):  bullets.extend(w.fire(player.rect))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if inventory.open:
                    inventory.handle_mousedown(event.pos, SCREEN_W, SCREEN_H)
                elif game_active and event.button == 1:
                    w = inventory.active_weapon
                    if isinstance(w, Sword):  w.swing(player.rect)
                    elif isinstance(w, Gun):  bullets.extend(w.fire(player.rect))

            elif event.type == pygame.MOUSEMOTION:
                if inventory.open:
                    inventory.handle_mousemotion(event.pos)
                    inventory.update_hover(event.pos, SCREEN_W, SCREEN_H)

            elif event.type == pygame.MOUSEBUTTONUP:
                if inventory.open:
                    inventory.handle_mouseup(event.pos, SCREEN_W, SCREEN_H)

        # ── INVENTORY SCREEN (game paused) ──────────────────────────
        if inventory.open:
            screen.fill(C_BG)
            for wall in walls: wall.draw(screen)
            inventory.draw(screen)
            pygame.display.flip()
            continue

        # ── END SCREEN ──────────────────────────────────────────────
        if not game_active:
            screen.fill(C_BG)
            for wall in walls: wall.draw(screen)
            for chest in chests: chest.draw(screen, font_sm)
            for m in monsters:
                if m.health > 0: m.draw(screen)
            player.draw(screen)
            draw_end_screen(screen, you_win, font_lg, font_sm)
            pygame.display.flip()
            continue

        # ── PLAYER MOVEMENT ─────────────────────────────────────────
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += player.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= player.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += player.speed
        if dx and dy:
            dx /= math.sqrt(2);  dy /= math.sqrt(2)

        player.move_with_walls(dx, dy, walls)
        player.rect.clamp_ip(pygame.Rect(TILE, TILE,
                                         SCREEN_W - TILE * 2, SCREEN_H - TILE * 2))
        player.update_invincibility()

        # ── WEAPON UPDATE ────────────────────────────────────────────
        weapon = inventory.active_weapon
        if isinstance(weapon, Sword): weapon.update(player.rect)
        elif isinstance(weapon, Gun): weapon.update_angle(player.rect)

        # ── CONTINUOUS FIRING (held F key) ──────────────────────────
        if pygame.key.get_pressed()[pygame.K_f] and game_active and not inventory.open:
            w = inventory.active_weapon
            if isinstance(w, Gun):  bullets.extend(w.fire(player.rect))
            elif isinstance(w, Sword): w.swing(player.rect)

        # ── BULLETS ─────────────────────────────────────────────────
        for b in bullets[:]:
            b.update(SCREEN_W, SCREEN_H)
            if not b.alive:
                bullets.remove(b);  continue
            for wall in walls:
                if b.get_rect().colliderect(wall.rect):
                    b.alive = False
                    if b in bullets: bullets.remove(b)
                    break

        # ── MONSTER AI (BFS pathfinding) ─────────────────────────────
        for m in monsters:
            if m.health > 0:
                m.move_towards_player(player.rect, walls, grid)
                m.rect.clamp_ip(pygame.Rect(TILE, TILE,
                                            SCREEN_W - TILE*2, SCREEN_H - TILE*2))

        # ── BULLET vs MONSTER ────────────────────────────────────────
        for b in bullets[:]:
            if not b.alive: continue
            for m in monsters:
                if m.health > 0 and b.get_rect().colliderect(m.rect):
                    m.health -= b.damage
                    b.alive   = False
                    if b in bullets: bullets.remove(b)
                    # Drop coins on kill
                    if m.health <= 0:
                        coins.extend(m.drop_coins())
                    break

        # ── SWORD vs MONSTER ─────────────────────────────────────────
        if isinstance(weapon, Sword):
            prev_hp = {id(m): m.health for m in monsters}
            weapon.check_hits(player.rect, monsters)
            for m in monsters:
                if m.health <= 0 and prev_hp.get(id(m), 0) > 0:
                    coins.extend(m.drop_coins())

        # ── PLAYER vs MONSTER ────────────────────────────────────────
        for m in monsters:
            if m.health > 0 and player.rect.colliderect(m.rect):
                player.take_damage(15)

        # ── COIN PHYSICS & COLLECTION ────────────────────────────────
        for coin in coins[:]:
            coin.update(walls)
            # Collect if player walks over it
            if coin.alive and player.rect.colliderect(coin.collect_rect()):
                player.money += coin.value
                coin.alive    = False
        coins = [c for c in coins if c.alive]

        # ── WIN / LOSE ───────────────────────────────────────────────
        if player.health <= 0:
            player.health = 0;  game_active = False;  game_over = True

        if monsters and all(m.health <= 0 for m in monsters):
            game_active = False;  you_win = True

        # ── DRAW ────────────────────────────────────────────────────
        screen.fill(C_BG)

        # Floor tiles (subtle contrast)
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c]:
                    pygame.draw.rect(screen, C_FLOOR,
                                     (c * TILE + 1, r * TILE + 1, TILE - 2, TILE - 2))

        for wall in walls:     wall.draw(screen)
        for chest in chests:   chest.draw(screen, font_sm)
        for coin in coins:     coin.draw(screen)
        for b in bullets:      b.draw(screen)

        for m in monsters:
            if m.health > 0:   m.draw(screen)

        player.draw(screen)
        
        # Draw ammo counter under player if wielding gun
        weapon = inventory.active_weapon
        if isinstance(weapon, Gun):
            ammo_str = f"mag {weapon.ammo_current}/{weapon.mag_size}"
            ammo_label = font_xs.render(ammo_str, True, C_YELLOW if weapon.ammo_current > 0 else C_RED)
            screen.blit(ammo_label, (player.rect.centerx - ammo_label.get_width() // 2, 
                                     player.rect.bottom + 4))

        if isinstance(weapon, Sword):    weapon.draw(screen, player.rect)
        elif isinstance(weapon, Gun):    weapon.draw(screen, player.rect)

        inventory.draw_hotbar(screen, font_sm)
        draw_hud(screen, player, chests, inventory, font_sm, font_xs)

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