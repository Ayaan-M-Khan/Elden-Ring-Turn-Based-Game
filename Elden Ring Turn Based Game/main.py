'''
Elden Ring Turn Based Game:
  Turn-based RPG inspired by Elden Ring.
  The player creates a character, explores areas, fights enemies and bosses,
  collects runes, shops for gear, and progresses through the story.
  player  — the human-controlled character (stats, attack, heal, cooldowns)
  Weapon  — weapon data and stats
  armor   — armor data and stats
  Heal    — flask/consumable data and quantity tracking
  monster — enemy character (stats drawn from ENEMY_TYPES dict, AI attack logic)

STORY LOOP:
  For each area:
    1. Narrative intro text
    2. Spawn 1-3 small enemies -> battle loop
    3. Spawn boss -> battle loop
    4. Award runes, open shop/rest
    5. Advance to next area


# -- Change log / TODO ---------------------------------------------------------
# * Change heals to flasks - k DONE
# - remove small and keep big/medium DONE
# * Create Bosses - A done
# - keep them around 100 (changed)
# - Make it so they drop runes  - k DONE (but fix so scalable)
# * Create shop -k (finish it up)
# - have a blacksmith that upgrades weapon/armor attribute with runes (maybe)
# * Create character classes - a
# - Armor/weapon/flasks done
# * Fix up enemies to be elden ring themed -a done
# * Create story loop - a/k done
# - enter area, fight small enemies, fight boss, rest and use shop, progress to next area done
# * Create story - a done
# * Fix defence stat to include weapon/armor defence stats - k (done)
# * Implement runes/money system - k (done)
'''


import os
import random
import time
import json
import storyline
from storyline import shop 

# Function delay(delay_time)
#   sleep the program for delay_time seconds
def delay(delay_time):
    time.sleep(delay_time)

# Function clear()
#  clear the terminal
def clear():
    # 'nt' means Windows, others (Mac/Linux) use 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')


# ── Save / Load System ─────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save.txt")

# Function save_game(area_index)
#   Serialises all critical player state into a JSON-formatted save.txt file.
#   Called after every boss defeat and after every shop visit.
#   PRE:  hero, weapon_stash, equipped_armor, heal_stash are initialised globals;
#         area_index is a non-negative int representing current story progress.
#   POST: save.txt is written (or overwritten) with the player's current state.
def save_game(area_index):
    data = {
        # ── Player core stats ──────────────────────────────────────────────────
        "name":       hero.name,
        "health":     hero.health,
        "max_health": hero.max_health,
        "runes":      hero.runes,
        "defense":    hero.defense,
        "speed":      hero.speed,
        "accuracy":   hero.accuracy,
        "crit_chance":  hero.crit_chance,
        "crit_damage":  hero.crit_damage,
        "heal_cooldown_remaining":   hero.heal_cooldown_remaining,
        "special_attack_cooldown":   hero.special_attack_cooldown,

        # ── Progress ───────────────────────────────────────────────────────────
        "area_index": area_index,

        # ── Inventory: all weapons in stash ───────────────────────────────────
        "weapons": [
            {
                "name":                  w.name,
                "attack_power":          w.attack_power,
                "speed":                 w.speed,
                "accuracy":              w.accuracy,
                "crit_chance":           w.crit_chance,
                "crit_damage":           w.crit_damage,
                "special_attack_name":   w.special_attack_name,
                "special_attack_damage": w.special_attack_damage,
                "cost":                  w.cost,
            }
            for w in weapon_stash
        ],

        # ── Equipped armor ────────────────────────────────────────────────────
        "armor": {
            "name":        equipped_armor.name,
            "defense":     equipped_armor.defense,
            "speed":       equipped_armor.speed,
            "crit_chance": equipped_armor.crit_chance,
            "crit_damage": equipped_armor.crit_damage,
            "cost":        equipped_armor.cost,
        },

        # ── Flasks ────────────────────────────────────────────────────────────
        "flask": {
            "heal_name":     heal_stash[0].heal_name,
            "heal_amount":   heal_stash[0].heal_amount,
            "heal_quantity": heal_stash[0].heal_quantity,
        },
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("\n[ ⚜  Progress saved at the Site of Grace. ]")


# Function load_game()
#   Reads save.txt and returns a dict of saved data, or None if no save exists.
#   PRE:  SAVE_FILE path is set.
#   POST: Returns the parsed save dict on success, or None if file is missing /
#         unreadable.
def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        print("Warning: save file is corrupt and will be ignored.")
        return None


# Function restore_from_save(data)
#   Rebuilds all global game objects from the dict returned by load_game().
#   PRE:  data is a valid save dict (keys match those written by save_game).
#   POST: hero, weapon_stash, equipped_armor, heal_stash are all restored;
#         returns the saved area_index so story_loop can resume from there.
def restore_from_save(data):
    global hero, weapon_stash, equipped_armor, heal_stash

    # ── Rebuild player ─────────────────────────────────────────────────────────
    hero = player(data["name"], data["health"], data["max_health"], data["runes"])
    hero.defense                  = data["defense"]
    hero.speed                    = data["speed"]
    hero.accuracy                 = data["accuracy"]
    hero.crit_chance              = data["crit_chance"]
    hero.crit_damage              = data["crit_damage"]
    hero.heal_cooldown_remaining  = data["heal_cooldown_remaining"]
    hero.special_attack_cooldown  = data["special_attack_cooldown"]

    # ── Rebuild weapon stash ───────────────────────────────────────────────────
    weapon_stash = [
        Weapon(
            w["name"], w["attack_power"], w["speed"], w["accuracy"],
            w["crit_chance"], w["crit_damage"],
            w["special_attack_name"], w["special_attack_damage"], w["cost"]
        )
        for w in data["weapons"]
    ]

    # ── Rebuild equipped armor ─────────────────────────────────────────────────
    a = data["armor"]
    equipped_armor = armor(
        a["name"], a["defense"], a["speed"], a["crit_chance"], a["crit_damage"], a["cost"]
    )

    # ── Rebuild flask ──────────────────────────────────────────────────────────
    fl = data["flask"]
    heal_stash = [Heal(fl["heal_name"], fl["heal_amount"], fl["heal_quantity"])]

    return data["area_index"]


# Class player
#   Constructor __init__(name, health, max_health, runes)
#     Store name, health, max_health, runes as attributes
#     Set attack_choice to "none"
#     Set defense, accuracy, crit_chance, crit_damage, heal_amount, heal_quantity to 0
#     Set speed to 10
#     Set heal_cooldown_remaining and special_attack_cooldown to 0
#
#   Method attack(target, attack_choice)
#     Set attack_power to 0
#     If attack_choice is "weapon"
#       Call get_valid_weapon() — if None, print cancel message and return False
#       Set attack_power to the weapon's attack_power
#     Else if attack_choice is "special attack"
#       If special_attack_cooldown > 0, print wait message and return False
#       Call get_valid_weapon() — if None, print cancel message and return False
#       Set attack_power to the weapon's special_attack_damage
#       Print special attack name, set special_attack_cooldown to 3
#     Else
#       Print "Invalid attack choice!" and return False
#     Subtract attack_power from target.health (floor at 0)
#     Print damage dealt and target's remaining health
#     Tick special_attack_cooldown down if active
#     Return True
#
#   Method get_valid_weapon()
#     Loop forever
#       If weapon_stash is empty, print "no weapons" and return None
#       Print all weapons in weapon_stash with their stats
#       Prompt user to choose a weapon name or "cancel"
#       If "cancel", return None
#       Search weapon_stash for a matching name (case-insensitive)
#       If found, return that Weapon object
#       Otherwise print "not found" and loop again
#
#   Method heal(target)
#     Call heal_cooldown() — if False, return False
#     If target is already at full health, print message and return False
#     Get the first flask from heal_stash
#     If flask.heal_quantity is 0, print "no flasks" and return False
#     Increase target.health by flask.heal_amount (cap at max_health)
#     Decrement flask.heal_quantity by 1
#     Set heal_cooldown_remaining to 2
#     Tick special_attack_cooldown down if active
#     Print heal result and return True
#
#   Method heal_cooldown()
#     If heal_cooldown_remaining <= 0, return True
#     Otherwise print wait message and return False
#
#   Method tick_cooldowns()
#     If heal_cooldown_remaining > 0, decrement by 1
class player:
    # PRE:  target is a monster object with a health attribute;
    #       if attack_choice is "weapon" or "special attack", weapon_stash must
    #       be non-empty and the player must select a valid weapon
    # POST: If the attack is valid and a weapon is selected (where required),
    #       target.health is reduced by attack_power (floored at 0),
    #       damage and remaining HP are printed, cooldowns are ticked,
    #       and True is returned.
    #       If the attack is invalid or weapon selection is cancelled, no
    #       damage is dealt and False is returned.
    def __init__(self, name, health, max_health, runes):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.runes = runes
        self.attack_choice = "none"
        self.defense = 0
        self.speed = 10
        self.accuracy = 0
        self.crit_chance = 0
        self.crit_damage = 0
        self.heal_amount = 0
        self.heal_quantity = 0
        self.heal_cooldown_remaining = 0
        self.special_attack_cooldown = 0


    def attack(self, target, attack_choice):
        attack_power = 0

        if attack_choice == "weapon":
            w = self.get_valid_weapon()
            if w is None:
                print("\nWeapon attack cancelled!")
                return False
            attack_power = w.attack_power

        elif attack_choice == "special attack":
            if self.special_attack_cooldown > 0:
                print(f"\nYou can't use your special attack yet!")
                print(f"Wait {self.special_attack_cooldown} more turn(s).")
                return False

            w = self.get_valid_weapon()
            if w is None:
                print("\nSpecial attack cancelled!")
                return False

            attack_power = w.special_attack_damage
            print(f"\n{self.name} uses {w.special_attack_name}!")
            self.special_attack_cooldown = 2

        else:
            print("Invalid attack choice!\n")
            return False

        target.health -= attack_power
        if target.health < 0:
            target.health = 0

        print(f"\n{self.name} damages the {target.name} for {attack_power} damage!")
        print(f"The {target.name} has {target.health} health left!\n")

        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1

        return True

    def get_valid_weapon(self):
        # PRE:  weapon_stash is a list (may be empty);
        #       the player will be prompted to type a weapon name or "cancel"
        # POST: Returns the matching Weapon object from weapon_stash if found,
        #       or None if the player types "cancel" or weapon_stash is empty
        while True:
            if not weapon_stash:
                print("\nYou have no weapons!")
                return None
            print("\nChoose a weapon to attack with:")
            print("\nAvailable weapons")
            for w in weapon_stash:
                print(f"  - {w.name}  (ATK: {w.attack_power}, Special: {w.special_attack_name} {w.special_attack_damage} DMG)")
            weapon_name = input("Choose a weapon (or 'cancel' to go back): ").strip()
            if weapon_name.lower() == "cancel":
                return None
            for w in weapon_stash:
                if w.name.lower() == weapon_name.lower():
                    return w
            print("Weapon not found — try again.")

    def heal(self, target):
        # PRE:  target is a player object with health and max_health attributes;
        #       heal_stash is non-empty and heal_stash[0] is a Heal object;
        #       self.heal_cooldown_remaining and target.health may be any values
        # POST: If the heal cooldown has expired, target is not at full health,
        #       and flasks remain, target.health is increased by flask.heal_amount
        #       (capped at max_health), flask.heal_quantity is decremented by 1,
        #       self.heal_cooldown_remaining is set to 2, and True is returned.
        #       Otherwise an appropriate message is printed and False is returned.
        if not self.heal_cooldown():
            return False

        if target.health >= target.max_health:
            print(f"\n{target.name} already has full health!")
            return False

        flask = heal_stash[0]  

        if flask.heal_quantity <= 0:
            print("\nYou have no flasks remaining!")
            return False

        target.health = min(target.health + flask.heal_amount, target.max_health)
        flask.heal_quantity -= 1
        print(f"\n{self.name} drinks a {flask.heal_name}!")
        print(f"{target.name} now has {target.health}/{target.max_health} HP.")
        print(f"Flasks remaining: {flask.heal_quantity}")
        self.heal_cooldown_remaining = 2
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1
        return True

    def heal_cooldown(self):
        # PRE:  self.heal_cooldown_remaining is a non-negative integer
        # POST: Returns True if heal_cooldown_remaining is 0 (heal is available);
        #       prints a wait message and returns False if cooldown is still active
        if self.heal_cooldown_remaining <= 0:
            return True
        else:
            print(f"You can't heal yet! Wait {self.heal_cooldown_remaining} more turn(s).")
            return False

    def tick_cooldowns(self):
        # PRE:  self.heal_cooldown_remaining is a non-negative integer
        # POST: If heal_cooldown_remaining > 0, it is decremented by 1;
        #       no return value
        if self.heal_cooldown_remaining > 0:
            self.heal_cooldown_remaining -= 1


# Class Weapon
#   Constructor __init__(name, attack_power, speed, accuracy,
#                        crit_chance, crit_damage, special_attack_name,
#                        special_attack_damage, cost)
#     Store all provided stats as attributes on the object
class Weapon:

    # PRE:  name is a string; attack_power, speed, cost are positive ints;
    #       accuracy, crit_chance are ints in [0, 100];
    #       crit_damage is a float >= 1.0;
    #       special_attack_name is a string; special_attack_damage is a positive int
    # POST: A Weapon object is created with all provided stats stored as attributes
    def __init__(self, name, attack_power, speed, accuracy,
                 crit_chance, crit_damage, special_attack_name, special_attack_damage, cost):
        self.name = name
        self.attack_power = attack_power
        self.speed = speed
        self.accuracy = accuracy
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        self.special_attack_name = special_attack_name
        self.special_attack_damage = special_attack_damage
        self.cost = cost


weapon_stash = [
    Weapon("Sword", 20, 10, 80, 15, 1.5, "Triple Slash", 30, 0)
]



# Class armor
#   Constructor __init__(name, defense, speed, crit_chance, crit_damage, cost)
#     Store all provided stats as attributes on the object
class armor:
    # PRE:  name is a string; defense and cost are non-negative ints;
    #       speed is an int (may be negative for heavy armor);
    #       crit_chance is an int in [0, 100]; crit_damage is a float >= 1.0
    # POST: An armor object is created with all provided stats stored as attributes
    def __init__(self, name, defense, speed, crit_chance, crit_damage, cost):
        self.name = name
        self.defense = defense
        self.speed = speed
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        self.cost = cost

armor_stash = [
    armor("Leather Armor", 10, 5, 5, 1.2, 0)
]

equipped_armor = armor_stash[0]




# Class Heal
#   Constructor __init__(heal_name, heal_amount, heal_quantity)
#     Store heal_name, heal_amount, and heal_quantity as attributes on the object
class Heal:
    # PRE:  heal_name is a string; heal_amount is a positive int;
    #       heal_quantity is a non-negative int
    # POST: A Heal object is created with the given name, heal amount,
    #       and remaining quantity stored as attributes
    def __init__(self, heal_name, heal_amount, heal_quantity):
        self.heal_name = heal_name
        self.heal_amount = heal_amount
        self.heal_quantity = heal_quantity


heal_stash = [
    Heal("Flask of Crimson Tears", 50, 6),
]

#  Area Data 







# Function display_player_stats(p)
#   Calculate total_def as p.defense + equipped_armor.defense
#   Calculate total_spd as p.speed + equipped_armor.speed
#   Get flask_quantity from heal_stash[0].heal_quantity
#   Print a formatted line showing name, HP, speed, defense, and flask count
def display_player_stats(p):
    # PRE:  p is a player object with defense, speed attributes;
    #       equipped_armor is a global armor object with defense and speed attributes;
    #       heal_stash is a non-empty list and heal_stash[0] has a heal_quantity attribute
    # POST: A single formatted line showing the player's name, HP, effective speed,
    #       effective defense, and remaining flask count is printed; no return value
    total_def = p.defense + equipped_armor.defense
    total_spd = p.speed + equipped_armor.speed
    flask_quantity = heal_stash[0].heal_quantity
    print(f"  {p.name} — HP: {p.health}/{p.max_health}  SPD: {total_spd}  DEF: {total_def}  Flasks: {flask_quantity}")


# Function display_monster_stats(m)
#   Print a formatted line showing the monster's name, HP, attack power,
#   defense, and speed
def display_monster_stats(m):
    # PRE:  m is a monster object with name, health, max_health, attack_power,
    #       defense, and speed attributes
    # POST: A single formatted line showing the monster's name, HP, attack power,
    #       defense, and speed is printed; no return value
    print(f"  {m.name} — HP: {m.health}/{m.max_health}  ATK: {m.attack_power}  DEF: {m.defense}  SPD: {m.speed}")


# Function prompt(text)
#   Clear the terminal screen
#   Print the given text
def prompt(text):
    clear()
    print(text)


# Function runesReward(enemy_type)
#   Award runes to the hero based on the enemy defeated
#   Bosses give 100 runes, small enemies give 10
def runesReward(enemy_type):
    reward = 10
    bosses = [
        "Margit, the Fell Omen", "Godrick the Grafted", "Rennala, Queen of the Full Moon",
        "Starscourge Radahn", "Rykard, Lord of Blasphemy", "Morgott, the Omen King",
        "Fire Giant", "Mohg, Lord of Blood", "Malenia, Blade of Miquella",
        "Maliketh, the Black Blade", "Godfrey / Hoarah Loux", "Radagon of the Golden Order",
        "Elden Beast"
    ]
    if enemy_type in bosses:
        reward = 100
    hero.runes += reward
    print(f"You gained {reward} runes! Total: {hero.runes}")


# ----- battle_loop -----------------------------------------------------------
def battle_loop(enemy):
    # PRE:  enemy is a monster object; hero, heal_stash, equipped_armor are globals;
    #       hero.health > 0 at the start of the call
    # POST: Runs a full turn-based battle; returns True if hero wins, False if hero dies
    hero_turn = hero.speed >= enemy.speed

    while hero.health > 0 and enemy.health > 0:
        delay(8)
        clear()
        print("=" * 40)
        display_monster_stats(enemy)
        display_player_stats(hero)
        print("=" * 40)

        if hero_turn:
            print(f"\n{hero.name}'s turn!")
            hero.tick_cooldowns()
            valid_turn = False
            while not valid_turn:
                action = input("Do you want to attack or heal? ").strip().lower()
                if action == "attack":
                    attack_choice = input("Choose an attack (weapon / special attack): ").strip().lower()
                    result = hero.attack(enemy, attack_choice)
                    if result:
                        valid_turn = True
                elif action == "heal":
                    healed = hero.heal(hero)
                    if healed:
                        valid_turn = True
                else:
                    print("Please type 'attack' or 'heal'.\n")
            hero_turn = False

        else:
            print(f"\n{enemy.name}'s turn!\n")
            delay(4)
            if random.randint(1, 4) == 1:
                enemy.special(hero)
            else:
                enemy.attack(hero)
            hero_turn = True
            if hero.health <= 0:
                break

    clear()
    if hero.health <= 0:
        print("\n💀 You have been defeated! Game over.")
        return False
    else:
        print(f"\n🏆 {enemy.name} FELLED")
        runesReward(enemy.enemy_type)
        delay(4)
        return True


# ----- ending_choice ---------------------------------------------------------
# Function ending_choice()
#   Print the final narrative and prompt player to choose "mend" or "destroy"
#   If "mend"  -> print Elden Lord ending
#   If "destroy" -> print Frenzied Flame ending
#   Loop until valid choice
def ending_choice():
    # PRE:  hero is a global player object with name and runes attributes;
    #       the Elden Beast has just been defeated
    # POST: Prints one of two endings based on player choice; game ends after this
    prompt(
        "The shards of the Ring hover before you. The fate of the Lands Between is yours to decide.\n"
        "What do you do?\n"
        "  mend    — Piece together the shattered remnants of the world. \n"
    "            Take your seat upon the Elden Throne and usher in a new Age of Order.\n"
        "  destroy — Surrender to the yellow flame of madness within. \n"
    "            Incinerate the Erdtree and the very concept of reality. May chaos take the world!\n"
    )
    while True:
        choice = input("Your choice (mend / destroy): ").strip().lower()
        if choice == "mend":
            prompt(
                "You gather the fractured shards, kneeling before the shattered husk of Marika.\n"
            "The Great Runes pulse with a pale gold, mending the laws of the world.\n"
            "The sky clears over the Ashen Capital, and the Erdtree’s glow returns—\n"
            "dimmer than before, but steady.\n\n"
            f"The fallen leaves tell a story of how {hero.name} became Elden Lord.\n"
            f"Runes held at the end of an age: {hero.runes}\n\n"
            "✨  ENDING: AGE OF ORDER  ✨\n\n"
            "        -- Thanks for playing! --\n"
            )
            break
        elif choice == "destroy":
            prompt(
                "You engulf the Ring with Frenzied Flames...\n"
                "The Erdtree screams. The sky cracks open.\n"
                "Three great eyes burn upon your brow.\n\n"
                f"You are {hero.name}, Lord of Frenzied Flame.\n"
                f"Runes collected: {hero.runes}\n\n"
                "🔥  ENDING: LORD OF FRENZIED FLAME  🔥\n\n"
                "        -- Thanks for playing! --\n"
            )
            break
        else:
            print("\nThe Ring waits. Choose: mend or destroy.")


# ----- story_loop ------------------------------------------------------------
# Function story_loop()
#   For each area in AREAS:
#     1. Print intro narrative
#     2. If enemies list not empty, sample 1-2 and run battle_loop for each
#     3. Print boss intro, spawn boss, run battle_loop
#     4. If ending flag set, call ending_choice() and return
#     5. Otherwise print rest text, refill flasks, restore health, open shop
def story_loop(start_index=0):
    # PRE:  hero, heal_stash, equipped_armor, storyline.AREAS are all initialized globals;
    #       hero.health > 0 at the start of the call;
    #       start_index is the index into storyline.AREAS to resume from (default 0).
    # POST: Steps the player through all areas in storyline.AREAS in order starting at
    #       start_index; saves after every boss defeat and shop; ends early if
    #       hero dies; calls ending_choice() on the final area.
    for area_index, area in enumerate(storyline.AREAS):

        # Skip areas already completed when resuming from a save
        if area_index < start_index:
            continue

        # ----- 1. Area intro -------------------------------------------------
        prompt(f"[ {area['name']} ]\n\n" + area["intro"])
        input("\nPress Enter to continue...")

        # ----- 2. Minion fights ----------------------------------------------
        if area["enemies"]:
            num_enemies = random.randint(1, min(2, len(area["enemies"])))
            small_pool = random.sample(area["enemies"], num_enemies)
            for enemy_type in small_pool:
                prompt(f"A {enemy_type} blocks your path!\n")
                delay(2)
                enemy = storyline.monster(enemy_type)
                if not battle_loop(enemy):
                    return

        # ----- 3. Boss intro -------------------------------------------------
        prompt(area["boss_intro"])
        input("\nPress Enter to continue...")

        # ----- 4. Boss fight -------------------------------------------------
        boss = storyline.monster(area["boss"])
        if not battle_loop(boss):
            return

        # ----- 5. Ending check -----------------------------------------------
        if area.get("ending"):
            ending_choice()
            return

        # ----- 6. Rest and shop ----------------------------------------------
        # Final two areas (Radagon, Elden Beast) skip the shop and refill
        # flasks to max instead so the player is ready for what lies ahead.
        if area.get("final_stretch"):
            prompt(area["rest_text"])
            hero.health = hero.max_health
            heal_stash[0].heal_quantity = 12
            print("\nGrace flows through you. Your flasks are replenished.")
            print(f"HP fully restored. Flasks: {heal_stash[0].heal_quantity}/12")
            # Save after the final-stretch rest (next area index)
            save_game(area_index + 1)
            input("\nPress Enter to continue...")
        else:
            prompt(area["rest_text"])
            hero.health = hero.max_health
            input("\nPress Enter to continue...")
            shop()
            # Save after the shop so purchased gear is persisted
            save_game(area_index + 1)


# ── Character creation ─────────────────────────────────────────────────────────
# Character Creation
#   Check for a save file first; if found, offer to continue or start fresh.
#   Otherwise proceed with normal name + class selection.
#   Build hero, weapon_stash, and equipped_armor based on class choice.
#   Print a welcome message displaying the hero's starting stats.
#   Set fight to False.
clear()

# ----- Save-file check -------------------------------------------------------
# Attempt to load an existing save.  If one exists, ask the player whether they
# want to continue where they left off.
_save_data  = load_game()
_resume_index = 0          # area index to pass into story_loop later
_loaded       = False      # flag: True if we restored from a save

if _save_data:
    print("Welcome back, this is where you left off. Continue? (yes/no)")
    print(f"  Tarnished : {_save_data['name']}")
    print(f"  Area      : {storyline.AREAS[min(_save_data['area_index'], len(storyline.AREAS)-1)]['name']}")
    print(f"  HP        : {_save_data['health']}/{_save_data['max_health']}")
    print(f"  Runes     : {_save_data['runes']}")
    while True:
        _cont = input("\nContinue? (yes/no): ").strip().lower()
        if _cont == "yes":
            _resume_index = restore_from_save(_save_data)
            _loaded = True
            print(f"\nWelcome back, {hero.name}. Grace guides you onward.")
            break
        elif _cont == "no":
            print("\nVery well — a new journey begins. The old save will be overwritten.")
            break
        else:
            print("Please type 'yes' or 'no'.")

# ----- Name validation (only for a new game) ---------------------------------
if not _loaded:
    while True:
        player_name = input("What is your name, Tarnished? ").strip()
        if not player_name:
            print("You must enter a name to continue.")
        elif not all(c.isalpha() or c.isspace() for c in player_name):
            print("Name must contain only letters and spaces.")
        else:
            break

# ----- Class selection (new game only) ---------------------------------------
if not _loaded:
    print("\nChoose your starting class:")
    print("  1. Vagabond    — High Health, strong Defense. A reliable fighter.")
    print("  2. Samurai     — High Speed, sharp Crit. Swift and deadly.")
    print("  3. Hero        — Massive Health, heavy Attacks. Slow but unstoppable.")
    print("  4. Warrior     — Balanced Speed and Attack. Dual-wield specialist.")
    print("  5. Astrologer  — Fragile but high Accuracy and Crit Damage. Glass cannon.")
    print("  6. Prophet     — Moderate stats with strong Healing. Flask cooldown reduced.")
    print("  7. Bandit      — High Crit Chance and Speed. Strikes fast and hard.")
    print("  8. Wretch      — No armor, no advantages. For the brave (or foolish).")

    while True:
        class_choice = input("\nEnter a number (1-8): ").strip()

        if class_choice == "1":
            # Vagabond — tanky, high defense
            hero = player(player_name, 130, 130, 100)
            hero.defense = 6
            hero.speed = 10
            weapon_stash = [Weapon("Longsword", 16, 10, 80, 15, 1.5, "Square Off", 26, 0)]
            equipped_armor = armor("Vagabond Knight Armor", 12, 3, 5, 1.2, 0)
            break

        elif class_choice == "2":
            # Samurai — fast, crit-focused
            hero = player(player_name, 95, 95, 100)
            hero.speed = 16
            weapon_stash = [Weapon("Uchigatana", 18, 14, 86, 18, 1.6, "Unsheathe", 37, 0)]
            equipped_armor = armor("Land of Reeds Armor", 8, 6, 8, 1.3, 0)
            break

        elif class_choice == "3":
            # Hero — massive HP, heavy hits, slow
            hero = player(player_name, 150, 150, 100)
            hero.defense = 4
            hero.speed = 7
            weapon_stash = [Weapon("Axe", 22, 7, 75, 10, 1.6, "Barbaric Roar", 36, 0)]
            equipped_armor = armor("Champion Armor", 10, 1, 4, 1.3, 0)
            break

        elif class_choice == "4":
            # Warrior — balanced speed and attack
            hero = player(player_name, 105, 105, 100)
            hero.speed = 14
            weapon_stash = [Weapon("Scimitar", 17, 13, 84, 16, 1.6, "Spinning Slash", 28, 0)]
            equipped_armor = armor("Warrior Armor", 8, 5, 7, 1.3, 0)
            break

        elif class_choice == "5":
            # Astrologer — glass cannon, high accuracy and crit damage
            hero = player(player_name, 80, 80, 100)
            hero.speed = 12
            weapon_stash = [Weapon("Astrologer's Staff", 14, 12, 94, 22, 2.0, "Glintstone Pebble", 28, 0)]
            equipped_armor = armor("Astrologer Robe", 4, 7, 12, 1.5, 0)
            break

        elif class_choice == "6":
            # Prophet — moderate stats, heal cooldown starts at 0 (already default)
            hero = player(player_name, 110, 110, 100)
            hero.defense = 3
            hero.speed = 11
            hero.heal_cooldown_remaining = 0
            weapon_stash = [Weapon("Short Spear", 15, 11, 82, 12, 1.5, "Sacred Blade", 26, 0)]
            equipped_armor = armor("Prophet Robe", 5, 6, 6, 1.3, 0)
            break

        elif class_choice == "7":
            # Bandit — high crit chance and speed, fragile
            hero = player(player_name, 88, 88, 100)
            hero.speed = 18
            weapon_stash = [Weapon("Dagger", 13, 18, 92, 28, 1.9, "Quickstep Stab", 24, 0)]
            equipped_armor = armor("Black Knife Armor", 6, 8, 14, 1.6, 0)
            break

        elif class_choice == "8":
            # Wretch — bare minimum everything
            hero = player(player_name, 85, 85, 100)
            hero.speed = 10
            weapon_stash = [Weapon("Club", 12, 10, 78, 8, 1.4, "Wild Strikes", 20, 0)]
            equipped_armor = armor("No Armor", 0, 0, 0, 1.0, 0)
            break

        else:
            print("Please enter a number between 1 and 8.")

print(f"\nWelcome, {hero.name}!")
print(f"HP: {hero.health}/{hero.max_health}  DEF: {hero.defense}  SPD: {hero.speed}\n")
fight = False


# ----- Story Introduction Loop (new game only) -------------------------------
# When loading a saved game we skip the tutorial intro fight entirely and jump
# straight into story_loop at the saved area.
if not _loaded:
    while True:
        answer = input(
            "\nThe fallen leaves tell a story of a Great Ring shattered and a Grace returned to the dead.\n"
            "You awaken as a Tarnished in the cold, oppressive silence of the Chapel of Anticipation.\n"
            "Beside you, a Finger Maiden lies slumped and still, her guidance lost to the dust.\n"
            "The air is stagnant, smelling of ancient stone and rotted silk.\n\n"
            "Two paths diverge within the ruins:\n"
            "— To the LEFT, a balcony overlooking the fog-blanketed cliffs of Limgrave.\n"
            "— To the RIGHT, a heavy iron gate leading toward a bridge of splintered wood.\n\n"
            "Which path do you choose? (left/right): "
        ).strip().lower()

        if answer == "left":
            prompt(
                "\nYou step onto the balcony. The Erdtree glows in the distance, a beacon of golden grace.\n"
                "As you gaze at the cliffs of the Lands Between, a many-limbed horror drops from the rafters!\n\n"
                "A Grafted Scion, a nightmare stitched from the fallen, screeches as it lands.\n"
                "You must defend your life, Tarnished!"
            )
            fight = True
            break

        elif answer == "right":
            prompt(
                "\nYou push through the iron gate. The bridge creaks and sways over the abyss below.\n"
                "A message in golden light etched on the floor reads: 'Though the path be broken, seek the Elden Ring.'\n"
                "A grotesque figure waits at the center, its golden blades ready to harvest your soul.\n\n"
                "A Grafted Scion blocks your path! Prepare for battle."
            )
            fight = True
            break

        else:
            print("\nThe Golden Order demands a choice. Seek the guidance of grace: left or right.")

# ----- Story Loop ------------------------------------------------------------
if _loaded:
    # Resume directly at the saved area — no intro fight needed
    delay(2)
    story_loop(start_index=_resume_index)
elif fight:
    delay(2)
    intro_enemy = storyline.monster("Grafted Scion")
    survived = battle_loop(intro_enemy)
    if survived:
        prompt(
            "The Grafted Scion crumbles.\n"
            "Grace guides you forward. The road to the Erdtree begins. You are now in the Lands of Between.\n"
        )
        delay(6)
        story_loop(start_index=0)
