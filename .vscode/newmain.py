import sys
import pygame
import math
import random

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H  = 900, 650
TILE                = 50
FPS                 = 60
DAMAGE_COOLDOWN     = 1000          # ms of player invincibility after a hit
SWORD_COOLDOWN      = 500           # ms between sword swings
SWORD_SWING_DUR     = 260           # ms the arc sweep lasts
SWORD_ARC           = math.pi * 0.9 # total sweep angle (radians)
CHEST_INTERACT_DIST = 70

# Colours
C_BG         = (18,  18,  28)
C_WALL       = (55,  55,  80)
C_WALL_EDGE  = (70,  70, 100)
C_PLAYER     = (80, 200, 120)
C_MONSTER    = (200,  70,  70)
C_BULLET     = (255, 240,  80)
C_SHOTBULLET = (255, 160,  40)
C_SWORD      = (180, 220, 255)
C_SWORD_SWING= (220, 255, 255)
C_CHEST      = (200, 160,  40)
C_CHEST_OPN  = ( 80,  55,  15)
C_WHITE      = (240, 240, 240)
C_GREEN      = ( 80, 220, 120)
C_RED        = (220,  70,  70)
C_YELLOW     = (255, 240,  80)
C_ORANGE     = (255, 160,  40)
C_BLUE       = ( 80, 160, 255)
C_GREY       = (120, 120, 140)
C_DARK       = ( 10,  10,  20)
C_PANEL      = ( 28,  28,  45)
C_PANEL_EDGE = ( 60,  60,  90)


# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────
def norm(dx, dy):
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d else (0.0, 0.0)


def spawn_away_from(avoid_rect, min_dist, margin, max_w, max_h, walls):
    """Pick a random position not too close to avoid_rect and not inside a wall."""
    for _ in range(300):
        x = random.randint(margin, max_w - margin - TILE)
        y = random.randint(margin, max_h - margin - TILE)
        r = pygame.Rect(x, y, TILE, TILE)
        if math.hypot(x - avoid_rect.centerx, y - avoid_rect.centery) < min_dist:
            continue
        if any(r.colliderect(w.rect) for w in walls):
            continue
        return x, y
    return max_w - 120, max_h - 120


# ─────────────────────────────────────────────
#  BASE ENTITY
# ─────────────────────────────────────────────
class GameEntity:
    def __init__(self, name, health, max_health, x, y, w=50, h=50):
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
        pygame.draw.rect(surface, (60, 0, 0),
                         (self.rect.x, self.rect.y - 9, bw, 5))
        pygame.draw.rect(surface, color,
                         (self.rect.x, self.rect.y - 9, int(bw * ratio), 5))


# ─────────────────────────────────────────────
#  WEAPON BASE
# ─────────────────────────────────────────────
class Weapon:
    def __init__(self, name, damage):
        self.name   = name
        self.damage = damage


# ─────────────────────────────────────────────
#  SWORD  — arc-sweep melee
# ─────────────────────────────────────────────
class Sword(Weapon):
    LENGTH = 44
    WIDTH  = 7

    def __init__(self):
        super().__init__("Sword", 30)
        self._last_swing   = -SWORD_COOLDOWN   # ready immediately on spawn
        self.base_angle    = 0.0               # direction at swing start
        self.current_angle = 0.0               # angle drawn this frame
        self.swinging      = False
        self._swing_start  = 0
        self._hit_set: set = set()             # monster ids hit this swing

    @property
    def on_cooldown(self):
        return pygame.time.get_ticks() - self._last_swing < SWORD_COOLDOWN

    def swing(self, player_rect):
        """Start an arc sweep toward the mouse."""
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
        """Advance sweep; rest pointing at mouse when idle."""
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
        """
        Sample many points along the current arc swept so far.
        Each monster can only be damaged once per swing (_hit_set guard).
        """
        if not self.swinging:
            return
        cx, cy = player_rect.center
        arc_start = self.base_angle - SWORD_ARC / 2
        arc_end   = self.current_angle
        samples   = 14

        for i in range(samples):
            t = i / max(samples - 1, 1)
            a = arc_start + (arc_end - arc_start) * t
            # Test multiple radii to cover the full blade width
            for reach_frac in (0.5, 0.75, 1.0, 1.1):
                reach = (14 + self.LENGTH) * reach_frac
                sx = cx + math.cos(a) * reach
                sy = cy + math.sin(a) * reach
                pt = pygame.Rect(sx - 7, sy - 7, 14, 14)
                for m in monsters:
                    if m.health > 0 and id(m) not in self._hit_set:
                        if pt.colliderect(m.rect):
                            m.health -= self.damage
                            self._hit_set.add(id(m))

    def draw(self, surface, player_rect):
        cx, cy = player_rect.center
        a      = self.current_angle
        color  = C_SWORD_SWING if self.swinging else C_SWORD

        # Ghost arc trail while swinging
        if self.swinging:
            arc_start = self.base_angle - SWORD_ARC / 2
            pts = []
            for i in range(17):
                t  = i / 16
                aa = arc_start + (self.current_angle - arc_start) * t
                r  = 14 + self.LENGTH
                pts.append((int(cx + math.cos(aa) * r),
                             int(cy + math.sin(aa) * r)))
            if len(pts) >= 2:
                pygame.draw.lines(surface, (100, 180, 255), False, pts, 2)

        # Blade
        bx = cx + math.cos(a) * 14
        by = cy + math.sin(a) * 14
        tx = cx + math.cos(a) * (14 + self.LENGTH)
        ty = cy + math.sin(a) * (14 + self.LENGTH)
        pygame.draw.line(surface, color, (int(bx), int(by)),
                         (int(tx), int(ty)), self.WIDTH)
        # Handle
        hx = cx + math.cos(a + math.pi) * 7
        hy = cy + math.sin(a + math.pi) * 7
        pygame.draw.line(surface, (160, 120, 60),
                         (int(cx), int(cy)), (int(hx), int(hy)), 5)


# ─────────────────────────────────────────────
#  BULLET
# ─────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage,
                 color=C_BULLET, radius=5):
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
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.radius)


# ─────────────────────────────────────────────
#  GUN
# ─────────────────────────────────────────────
class Gun(Weapon):
    TYPES = {
        "Pistol":    dict(damage=20, speed=9,  fire_rate=400, spread=0,
                          bps=1, color=C_BULLET,    radius=5, barrel=24),
        "Shotgun":   dict(damage=15, speed=7,  fire_rate=800, spread=0.35,
                          bps=5, color=C_SHOTBULLET, radius=4, barrel=28),
        "RapidFire": dict(damage=10, speed=11, fire_rate=120, spread=0.08,
                          bps=1, color=C_BLUE,      radius=4, barrel=20),
    }

    def __init__(self, gun_type="Pistol"):
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

    @property
    def on_cooldown(self):
        return pygame.time.get_ticks() - self._last_shot < self.fire_rate

    def update_angle(self, player_rect):
        mx, my = pygame.mouse.get_pos()
        px, py = player_rect.center
        self.angle = math.atan2(my - py, mx - px)

    def fire(self, player_rect):
        if self.on_cooldown:
            return []
        self._last_shot = pygame.time.get_ticks()
        cx, cy = player_rect.center
        out = []
        for _ in range(self.bps):
            a = self.angle + random.uniform(-self.spread, self.spread)
            out.append(Bullet(cx, cy, math.cos(a), math.sin(a),
                              self.speed, self.damage, self.color, self.radius))
        return out

    def draw(self, surface, player_rect):
        cx, cy = player_rect.center
        ex = cx + math.cos(self.angle) * self.barrel
        ey = cy + math.sin(self.angle) * self.barrel
        pygame.draw.line(surface, C_GREY,
                         (int(cx), int(cy)), (int(ex), int(ey)), 6)
        pygame.draw.circle(surface, C_WHITE, (int(ex), int(ey)), 4)


# ─────────────────────────────────────────────
#  INVENTORY  — two-panel layout
# ─────────────────────────────────────────────
def _draw_panel(surface, x, y, w, h):
    pygame.draw.rect(surface, C_PANEL,      (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, C_PANEL_EDGE, (x, y, w, h), 1, border_radius=10)


class Inventory:
    """
    Two-panel inventory screen (opened with TAB):
      LEFT  panel — Equipped weapon slot + armour placeholder
      RIGHT panel — All collected items; click or press 1-9 to equip
    """

    def __init__(self):
        self.items        = []
        self.active_index = 0
        self.open         = False
        self._font_lg     = None
        self._font_sm     = None
        self._font_xs     = None

    def init_fonts(self):
        self._font_lg = pygame.font.SysFont(None, 30)
        self._font_sm = pygame.font.SysFont(None, 22)
        self._font_xs = pygame.font.SysFont(None, 18)

    # ── item management ──────────────────────
    def add(self, weapon):
        self.items.append(weapon)

    @property
    def active_weapon(self):
        if not self.items:
            return None
        return self.items[self.active_index % len(self.items)]

    def select(self, index):
        if 0 <= index < len(self.items):
            self.active_index = index

    def next_weapon(self):
        if self.items:
            self.active_index = (self.active_index + 1) % len(self.items)

    def prev_weapon(self):
        if self.items:
            self.active_index = (self.active_index - 1) % len(self.items)

    def toggle(self):
        self.open = not self.open

    # ── click to equip from right panel ──────
    def handle_click(self, mouse_pos, sw, sh):
        panel_y  = 60
        rx       = sw // 2 + 10
        rw       = sw - rx - 40
        item_y0  = panel_y + 72
        row_h    = 44
        pad      = 14
        for i in range(len(self.items)):
            iy       = item_y0 + i * row_h
            row_rect = pygame.Rect(rx + pad - 4, iy - 2, rw - pad * 2 + 4, row_h - 4)
            if row_rect.collidepoint(mouse_pos):
                self.active_index = i
                return True
        return False

    # ── full overlay draw ─────────────────────
    def draw(self, surface):
        if self._font_lg is None:
            self.init_fonts()
        sw, sh   = surface.get_size()
        panel_h  = sh - 100
        panel_y  = 60
        pad      = 14
        divider  = sw // 2

        # Dark backdrop
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((8, 8, 18, 215))
        surface.blit(ov, (0, 0))

        # ── TOP TITLE ────────────────────────
        bar = self._font_lg.render(
            "── CHARACTER  (TAB to close) ──", True, C_WHITE)
        surface.blit(bar, (sw // 2 - bar.get_width() // 2, 18))

        # ── LEFT PANEL — Equipped ────────────
        lx = 40
        lw = divider - lx - 20
        _draw_panel(surface, lx, panel_y, lw, panel_h)

        hdr_eq = self._font_lg.render("EQUIPPED", True, C_YELLOW)
        surface.blit(hdr_eq, (lx + lw // 2 - hdr_eq.get_width() // 2,
                               panel_y + pad))

        # Weapon slot
        wlabel = self._font_xs.render("WEAPON SLOT", True, C_GREY)
        surface.blit(wlabel, (lx + pad, panel_y + 52))
        slot_r = pygame.Rect(lx + pad, panel_y + 68, lw - pad * 2, 66)
        pygame.draw.rect(surface, (35, 35, 55), slot_r, border_radius=6)
        pygame.draw.rect(surface, C_PANEL_EDGE, slot_r, 1, border_radius=6)

        weapon = self.active_weapon
        if weapon:
            wname = self._font_sm.render(weapon.name, True, C_WHITE)
            surface.blit(wname, (slot_r.x + 10, slot_r.y + 8))
            if isinstance(weapon, Gun):
                stat = (f"DMG {weapon.damage}   SPD {weapon.speed}"
                        f"   RATE {weapon.fire_rate}ms")
            elif isinstance(weapon, Sword):
                stat = f"DMG {weapon.damage}   Arc melee sweep"
            else:
                stat = ""
            wstat = self._font_xs.render(stat, True, C_GREY)
            surface.blit(wstat, (slot_r.x + 10, slot_r.y + 36))
            # colour swatch
            sw_col = (C_SWORD if isinstance(weapon, Sword)
                      else weapon.color if isinstance(weapon, Gun)
                      else C_WHITE)
            pygame.draw.rect(surface, sw_col,
                             (slot_r.right - 22, slot_r.y + 18, 12, 30),
                             border_radius=3)
        else:
            etxt = self._font_xs.render("Empty", True, C_GREY)
            surface.blit(etxt, (slot_r.x + 10, slot_r.y + 24))

        # Armour slot (placeholder)
        alabel = self._font_xs.render("ARMOUR SLOT  (none)", True, C_GREY)
        surface.blit(alabel, (lx + pad, panel_y + 148))
        arm_r = pygame.Rect(lx + pad, panel_y + 164, lw - pad * 2, 52)
        pygame.draw.rect(surface, (30, 30, 50), arm_r, border_radius=6)
        pygame.draw.rect(surface, (50, 50, 70), arm_r, 1, border_radius=6)
        atxt = self._font_xs.render("No armour equipped", True, (70, 70, 90))
        surface.blit(atxt, (arm_r.x + 10, arm_r.y + 16))

        # Controls hint
        hints = ["1-9  equip item", "Q / E  cycle weapon", "TAB  close inventory"]
        for i, h in enumerate(hints):
            t = self._font_xs.render(h, True, C_GREY)
            surface.blit(t, (lx + pad, panel_y + panel_h - 76 + i * 20))

        # ── RIGHT PANEL — Items ───────────────
        rx = divider + 20
        rw = sw - rx - 40
        _draw_panel(surface, rx, panel_y, rw, panel_h)

        hdr_it = self._font_lg.render("INVENTORY", True, C_YELLOW)
        surface.blit(hdr_it, (rx + rw // 2 - hdr_it.get_width() // 2,
                               panel_y + pad))

        cnt = self._font_xs.render(f"{len(self.items)} item(s)", True, C_GREY)
        surface.blit(cnt, (rx + rw - cnt.get_width() - pad, panel_y + pad + 4))

        # Column header
        col_hdr = self._font_xs.render(
            "  #   Name                      DMG   Type", True, C_GREY)
        surface.blit(col_hdr, (rx + pad, panel_y + 50))
        pygame.draw.line(surface, C_PANEL_EDGE,
                         (rx + pad, panel_y + 64),
                         (rx + rw - pad, panel_y + 64))

        if not self.items:
            etxt = self._font_sm.render("No items yet.", True, C_GREY)
            surface.blit(etxt, (rx + rw // 2 - etxt.get_width() // 2,
                                 panel_y + 100))
        else:
            item_y0 = panel_y + 72
            row_h   = 44
            for i, item in enumerate(self.items):
                iy     = item_y0 + i * row_h
                active = (i == self.active_index % len(self.items))
                row_r  = pygame.Rect(rx + pad - 4, iy - 2,
                                     rw - pad * 2 + 4, row_h - 4)

                if active:
                    pygame.draw.rect(surface, (45, 45, 75), row_r,
                                     border_radius=5)
                    pygame.draw.rect(surface, C_YELLOW, row_r, 1,
                                     border_radius=5)

                # Colour swatch
                swatch = (C_SWORD if isinstance(item, Sword)
                          else item.color if isinstance(item, Gun)
                          else C_WHITE)
                pygame.draw.rect(surface, swatch,
                                 (rx + pad, iy + 9, 8, 22), border_radius=2)

                # Badge
                num_c = C_YELLOW if active else C_GREY
                num   = self._font_xs.render(f"[{i+1}]", True, num_c)
                surface.blit(num, (rx + pad + 14, iy + 13))

                # Name
                name_c = C_WHITE if active else (180, 180, 200)
                name   = self._font_sm.render(item.name, True, name_c)
                surface.blit(name, (rx + pad + 44, iy + 6))

                # Sub-line stats
                if isinstance(item, Gun):
                    sub = (f"DMG {item.damage}  "
                           f"Rate {item.fire_rate}ms  Spd {item.speed}")
                elif isinstance(item, Sword):
                    sub = f"DMG {item.damage}  Arc sweep melee"
                else:
                    sub = ""
                sub_t = self._font_xs.render(sub, True, C_GREY)
                surface.blit(sub_t, (rx + pad + 44, iy + 26))

                # Equipped badge
                if active:
                    eq = self._font_xs.render("EQUIPPED", True, C_GREEN)
                    surface.blit(eq, (rx + rw - eq.get_width() - pad * 2,
                                      iy + 13))

    # ── in-game hotbar ───────────────────────
    def draw_hotbar(self, surface):
        if self._font_sm is None:
            self.init_fonts()
        if not self.items:
            return
        sw, sh = surface.get_size()
        w = self.active_weapon
        t = self._font_sm.render(f"Weapon: {w.name}", True, C_YELLOW)
        surface.blit(t, (sw // 2 - t.get_width() // 2, sh - 28))


# ─────────────────────────────────────────────
#  WALL
# ─────────────────────────────────────────────
class Wall:
    def __init__(self, x, y, w=TILE, h=TILE):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, C_WALL,      self.rect)
        pygame.draw.rect(surface, C_WALL_EDGE, self.rect, 2)


def build_maze(screen_w, screen_h):
    walls = []
    cols  = screen_w // TILE
    rows  = screen_h // TILE

    # Border
    for c in range(cols):
        walls.append(Wall(c * TILE, 0))
        walls.append(Wall(c * TILE, (rows - 1) * TILE))
    for r in range(1, rows - 1):
        walls.append(Wall(0, r * TILE))
        walls.append(Wall((cols - 1) * TILE, r * TILE))

    # Interior tile coordinates (col, row)
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
        wx, wy = c * TILE, r * TILE
        if wx + TILE < screen_w and wy + TILE < screen_h:
            walls.append(Wall(wx, wy))
    return walls


# ─────────────────────────────────────────────
#  CHEST
# ─────────────────────────────────────────────
class Chest:
    LOOT_TABLE = [
        lambda: Gun("Shotgun"),
        lambda: Gun("RapidFire"),
        lambda: Gun("Pistol"),
        lambda: Sword(),
    ]

    def __init__(self, x, y):
        self.rect   = pygame.Rect(x, y, TILE, TILE)
        self.opened = False
        self.loot   = random.choice(self.LOOT_TABLE)()

    def try_open(self, player_rect):
        if self.opened:
            return None
        dist = math.hypot(self.rect.centerx - player_rect.centerx,
                          self.rect.centery - player_rect.centery)
        if dist <= CHEST_INTERACT_DIST:
            self.opened = True
            return self.loot
        return None

    def draw(self, surface, font):
        if self.opened:
            # Empty open chest — dark hollow appearance
            pygame.draw.rect(surface, C_CHEST_OPN, self.rect, border_radius=6)
            pygame.draw.rect(surface, (100, 70, 20), self.rect, 2, border_radius=6)
            # Open lid line across top
            pygame.draw.line(surface, (130, 90, 25),
                             (self.rect.left + 4,  self.rect.top + 7),
                             (self.rect.right - 4, self.rect.top + 7), 3)
            # "empty" label
            e = font.render("empty", True, (90, 65, 25))
            surface.blit(e, (self.rect.x + 5, self.rect.y + 18))
        else:
            # Closed chest
            pygame.draw.rect(surface, C_CHEST, self.rect, border_radius=6)
            pygame.draw.rect(surface, (255, 210, 80), self.rect, 2, border_radius=6)
            cx, cy = self.rect.center
            pygame.draw.circle(surface, (40, 30, 10), (cx, cy - 2), 7)
            pygame.draw.rect(surface,   (40, 30, 10), (cx - 6, cy + 3, 12, 10))


# ─────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────
class Player(GameEntity):
    def __init__(self, name, health, max_health, x, y, w=40, h=40):
        super().__init__(name, health, max_health, x, y, w, h)
        self.speed          = 4
        self._last_hit_time = -DAMAGE_COOLDOWN
        self.invincible     = False
        self._inv_end       = 0

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
        """Axis-separated so the player can slide along walls."""
        self.rect.x += int(dx)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if dx > 0:
                    self.rect.right = w.rect.left
                else:
                    self.rect.left  = w.rect.right

        self.rect.y += int(dy)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if dy > 0:
                    self.rect.bottom = w.rect.top
                else:
                    self.rect.top    = w.rect.bottom

    def draw(self, surface):
        flash = self.invincible and (pygame.time.get_ticks() // 100) % 2
        color = (255, 255, 255) if flash else C_PLAYER
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        self.draw_health_bar(surface, C_GREEN)


# ─────────────────────────────────────────────
#  MONSTER
# ─────────────────────────────────────────────
class Monster(GameEntity):
    def __init__(self, name, health, max_health, x, y, w=44, h=44):
        super().__init__(name, health, max_health, x, y, w, h)
        self.speed          = 2.2
        self.vx             = 0.0
        self.vy             = 0.0
        self._stuck_frames  = 0
        self._wander_angle  = random.uniform(0, math.pi * 2)
        self._wander_until  = 0
        self._prev_pos      = (float(x), float(y))

    def move_towards_player(self, px, py, walls):
        """
        Chase player using axis-separated wall resolution.
        A stuck-detection system triggers a random wander to escape corners.
        """
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        nx, ny = norm(dx, dy)
        now    = pygame.time.get_ticks()

        # Stuck detection: if barely moved in last frame, increment counter
        moved = math.hypot(self.rect.x - self._prev_pos[0],
                           self.rect.y - self._prev_pos[1])
        self._stuck_frames = (self._stuck_frames + 1) if moved < 0.6 else 0
        self._prev_pos     = (float(self.rect.x), float(self.rect.y))

        # If stuck 30+ frames, wander in a random direction for a while
        if self._stuck_frames > 30:
            if now > self._wander_until:
                self._wander_angle = random.uniform(0, math.pi * 2)
                self._wander_until = now + random.randint(300, 600)
            nx = math.cos(self._wander_angle)
            ny = math.sin(self._wander_angle)
            if self._stuck_frames > 100:   # hard reset after prolonged stuck
                self._stuck_frames = 0

        move_x = nx * self.speed
        move_y = ny * self.speed

        # ── X ──────────────────────────────────
        self.rect.x += int(move_x)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_x > 0:
                    self.rect.right = w.rect.left
                else:
                    self.rect.left  = w.rect.right

        # ── Y ──────────────────────────────────
        self.rect.y += int(move_y)
        for w in walls:
            if self.rect.colliderect(w.rect):
                if move_y > 0:
                    self.rect.bottom = w.rect.top
                else:
                    self.rect.top    = w.rect.bottom

    def draw(self, surface):
        pygame.draw.rect(surface, C_MONSTER, self.rect, border_radius=5)
        ex = self.rect.x + 10
        ey = self.rect.y + 12
        pygame.draw.circle(surface, C_YELLOW,   (ex,      ey), 4)
        pygame.draw.circle(surface, C_YELLOW,   (ex + 20, ey), 4)
        pygame.draw.circle(surface, (40, 0, 0), (ex +  1, ey), 2)
        pygame.draw.circle(surface, (40, 0, 0), (ex + 21, ey), 2)
        self.draw_health_bar(surface, C_RED)


# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────
def draw_hud(surface, player, inventory, chests, font_sm):
    sw, sh = surface.get_size()

    # Health bar — bottom left
    bar_w, bar_h = 200, 18
    bx, by       = 14, sh - 34
    ratio        = max(0.0, player.health / player.max_health)
    pygame.draw.rect(surface, (60, 0, 0),  (bx, by, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, C_GREEN,     (bx, by, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(surface, C_WHITE,     (bx, by, bar_w, bar_h), 1, border_radius=4)
    hp = font_sm.render(f"HP {max(0, player.health)}/{player.max_health}", True, C_WHITE)
    surface.blit(hp, (bx + 4, by + 2))

    # Chest prompt
    for chest in chests:
        if not chest.opened:
            dist = math.hypot(chest.rect.centerx - player.rect.centerx,
                              chest.rect.centery - player.rect.centery)
            if dist <= CHEST_INTERACT_DIST:
                p = font_sm.render("[E] Open chest", True, C_YELLOW)
                surface.blit(p, (chest.rect.x - 6, chest.rect.y - 22))

    # Controls strip — top centre
    ctrl = font_sm.render(
        "WASD move  |  Click/F attack  |  TAB inventory  |  E chest  |  1-3 weapon",
        True, C_GREY)
    surface.blit(ctrl, (sw // 2 - ctrl.get_width() // 2, 6))


def draw_end_screen(surface, won, font_lg, font_sm):
    sw, sh = surface.get_size()
    ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 165))
    surface.blit(ov, (0, 0))
    if won:
        t = font_lg.render("★  YOU WIN!  ★",           True, C_GREEN)
        s = font_sm.render("R to restart  |  ESC quit", True, C_WHITE)
    else:
        t = font_lg.render("✖  GAME OVER",             True, C_RED)
        s = font_sm.render("R to restart  |  ESC quit", True, C_WHITE)
    surface.blit(t, (sw // 2 - t.get_width() // 2, sh // 2 - 50))
    surface.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 + 14))


# ─────────────────────────────────────────────
#  LEVEL FACTORY
# ─────────────────────────────────────────────
def make_level(walls):
    player = Player("Hero", 100, 100, x=80, y=80)

    monsters = []
    for i in range(3):
        mx, my = spawn_away_from(player.rect, 250, TILE * 2,
                                 SCREEN_W, SCREEN_H, walls)
        monsters.append(Monster(f"Monster{i}", 60 + i * 20, 60 + i * 20, mx, my))

    chests = []
    for _ in range(4):
        cx, cy = spawn_away_from(player.rect, 120, TILE * 2,
                                 SCREEN_W, SCREEN_H, walls)
        chests.append(Chest(cx, cy))

    return player, monsters, chests


def fresh_inventory():
    """Starting loadout — Sword + Pistol only, no duplicates."""
    inv = Inventory()
    inv.init_fonts()
    inv.add(Sword())
    inv.add(Gun("Pistol"))
    return inv


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
def run():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Dungeon Brawler")
    clock   = pygame.time.Clock()
    font_sm = pygame.font.SysFont(None, 22)
    font_lg = pygame.font.SysFont(None, 42)

    walls     = build_maze(SCREEN_W, SCREEN_H)
    inventory = fresh_inventory()
    player, monsters, chests = make_level(walls)

    bullets     = []
    game_active = True
    game_over   = False
    you_win     = False

    running = True
    while running:
        clock.tick(FPS)

        # ── EVENTS ────────────────────────────
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
                    inventory = fresh_inventory()
                    bullets.clear()
                    player, monsters, chests = make_level(walls)
                    game_active = True
                    game_over   = False
                    you_win     = False

                # Weapon hotkeys — only outside inventory
                elif pygame.K_1 <= k <= pygame.K_9 and not inventory.open:
                    inventory.select(k - pygame.K_1)

                elif k == pygame.K_q and not inventory.open:
                    inventory.prev_weapon()

                elif k == pygame.K_e and not inventory.open:
                    # Open chest if nearby; otherwise cycle weapon
                    opened_chest = False
                    for chest in chests:
                        if not chest.opened:
                            dist = math.hypot(
                                chest.rect.centerx - player.rect.centerx,
                                chest.rect.centery - player.rect.centery)
                            if dist <= CHEST_INTERACT_DIST:
                                loot = chest.try_open(player.rect)
                                if loot:
                                    inventory.add(loot)
                                opened_chest = True
                                break
                    if not opened_chest:
                        inventory.next_weapon()

                # Attack with F
                elif k == pygame.K_f and game_active and not inventory.open:
                    w = inventory.active_weapon
                    if isinstance(w, Sword):
                        w.swing(player.rect)
                    elif isinstance(w, Gun):
                        bullets.extend(w.fire(player.rect))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if inventory.open:
                        inventory.handle_click(event.pos, SCREEN_W, SCREEN_H)
                    elif game_active:
                        w = inventory.active_weapon
                        if isinstance(w, Sword):
                            w.swing(player.rect)
                        elif isinstance(w, Gun):
                            bullets.extend(w.fire(player.rect))

        # ── INVENTORY PAUSE SCREEN ────────────
        if inventory.open:
            screen.fill(C_BG)
            for wall in walls:
                wall.draw(screen)
            inventory.draw(screen)
            pygame.display.flip()
            continue

        # ── END SCREEN ────────────────────────
        if not game_active:
            screen.fill(C_BG)
            for wall in walls:
                wall.draw(screen)
            for chest in chests:
                chest.draw(screen, font_sm)
            for m in monsters:
                if m.health > 0:
                    m.draw(screen)
            player.draw(screen)
            draw_end_screen(screen, you_win, font_lg, font_sm)
            pygame.display.flip()
            continue

        # ── PLAYER MOVEMENT ───────────────────
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += player.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= player.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += player.speed
        if dx and dy:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        player.move_with_walls(dx, dy, walls)
        player.rect.clamp_ip(
            pygame.Rect(TILE, TILE, SCREEN_W - TILE * 2, SCREEN_H - TILE * 2))
        player.update_invincibility()

        # ── WEAPON UPDATE ─────────────────────
        weapon = inventory.active_weapon
        if isinstance(weapon, Sword):
            weapon.update(player.rect)
        elif isinstance(weapon, Gun):
            weapon.update_angle(player.rect)

        # ── BULLET UPDATE ─────────────────────
        for b in bullets[:]:
            b.update(SCREEN_W, SCREEN_H)
            if not b.alive:
                bullets.remove(b)
                continue
            for wall in walls:
                if b.get_rect().colliderect(wall.rect):
                    b.alive = False
                    if b in bullets:
                        bullets.remove(b)
                    break

        # ── MONSTER AI ────────────────────────
        for m in monsters:
            if m.health > 0:
                m.move_towards_player(
                    player.rect.centerx, player.rect.centery, walls)
                m.rect.clamp_ip(
                    pygame.Rect(TILE, TILE,
                                SCREEN_W - TILE * 2, SCREEN_H - TILE * 2))

        # ── BULLET vs MONSTER ─────────────────
        for b in bullets[:]:
            if not b.alive:
                continue
            for m in monsters:
                if m.health > 0 and b.get_rect().colliderect(m.rect):
                    m.health -= b.damage
                    b.alive   = False
                    if b in bullets:
                        bullets.remove(b)
                    break

        # ── SWORD ARC vs MONSTER ─────────────
        if isinstance(weapon, Sword):
            weapon.check_hits(player.rect, monsters)

        # ── PLAYER vs MONSTER (cooldown) ──────
        for m in monsters:
            if m.health > 0 and player.rect.colliderect(m.rect):
                player.take_damage(15)

        # ── WIN / LOSE ────────────────────────
        if player.health <= 0:
            player.health = 0
            game_active   = False
            game_over     = True

        if monsters and all(m.health <= 0 for m in monsters):
            game_active = False
            you_win     = True

        # ── DRAW ──────────────────────────────
        screen.fill(C_BG)

        for wall in walls:
            wall.draw(screen)

        for chest in chests:
            chest.draw(screen, font_sm)

        for b in bullets:
            b.draw(screen)

        for m in monsters:
            if m.health > 0:
                m.draw(screen)

        player.draw(screen)

        if isinstance(weapon, Sword):
            weapon.draw(screen, player.rect)
        elif isinstance(weapon, Gun):
            weapon.draw(screen, player.rect)

        inventory.draw_hotbar(screen)
        draw_hud(screen, player, inventory, chests, font_sm)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Game error:", e)
        pygame.quit()
        sys.exit(1)