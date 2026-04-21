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

# Function delay(delay_time)
#   sleep the program for delay_time seconds
def delay(delay_time):
    time.sleep(delay_time)

# Function clear()
#  clear the terminal
def clear():
    # 'nt' means Windows, others (Mac/Linux) use 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')


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
# Weapons are sorted by cost — early cheap weapons for early areas,
# late expensive weapons for later areas. ATK scales from ~22 to ~55,
# specials scale from ~35 to ~100, costs from 800 to 18000.
weapon_storage = [
    # ----- Class starter weapons (cost 0, not sold in shop — for reference) ---
    # These are held at start and not listed in the shop.
    # Listed here so the shop can avoid duplicating them.

    # ----- Tier 1: Early game (Areas 1-2, cost 800-2000) ----------------------
    Weapon("Uchigatana",                 22, 14, 86, 18, 1.6, "Unsheathe",                 35,   800),
    Weapon("Lordsworn's Straight Sword", 24, 10, 80, 15, 1.5, "Square Off",               38,  1000),
    Weapon("Reduvia",                    26, 18, 92, 20, 1.7, "Reduvia Blood Blade",       42,  1500),
    Weapon("Nagakiba",                   28, 12, 84, 19, 1.7, "Piercing Draw",             44,  2000),
    Weapon("Axe",                        24,  8, 78, 12, 1.6, "Barbaric Roar",              38,  1000),
    Weapon("Scimitar",                   22, 13, 84, 16, 1.6, "Spinning Slash",             36,   850),
    Weapon("Short Spear",                21, 11, 82, 13, 1.5, "Sacred Blade",               34,   800),
    Weapon("Club",                       20,  9, 79,  9, 1.4, "Wild Strikes",               32,   750),
    Weapon("Dagger",                    18, 17, 91, 26, 1.9, "Quickstep Stab",             30,  1100),
    Weapon("Astrologer's Staff",        19, 12, 94, 22, 2.0, "Glintstone Pebble",           32, 950),
    # -- Sorcery / Incantation staves & seals (Tier 1) -------------------------
    Weapon("Glintstone Staff",           20, 13, 95, 22, 2.0, "Glintstone Pebble",         36,   900),
    Weapon("Finger Seal",                21, 11, 88, 16, 1.8, "Catch Flame",               34,  1200),
    Weapon("Crystal Staff",              25, 12, 96, 24, 2.0, "Crystal Barrage",           42,  1800),

    # ----- Tier 2: Mid game (Areas 3-5, cost 3000-6000) ----------------------
    Weapon("Godskin Peeler",             31, 17, 89, 21, 1.7, "Black Flame Tornado",       50,  3000),
    Weapon("Envoy's Long Horn",          30,  8, 79, 13, 1.6, "Bubble Shower",             48,  3500),
    Weapon("Eleonora's Poleblade",       33, 16, 87, 24, 1.8, "Bloodblade Dance",          54,  4000),
    Weapon("Moonveil",                   35, 14, 88, 22, 1.8, "Transient Moonlight",       58,  4500),
    Weapon("Rivers of Blood",            34, 15, 85, 24, 1.9, "Corpse Piler",              60,  5000),
    Weapon("Wing of Astel",              36, 15, 90, 23, 1.8, "Nebula",                    62,  5500),
    Weapon("Bolt of Gransax",            38, 11, 84, 17, 1.8, "Ancient Lightning Spear",   64,  6000),
    # -- Sorcery / Incantation staves & seals (Tier 2) -------------------------
    Weapon("Carian Glintblade Staff",    32, 13, 97, 26, 2.1, "Carian Glintblade",         52,  3200),
    Weapon("Meteorite Staff",            34, 10, 96, 24, 2.1, "Rock Sling",                56,  3800),
    Weapon("Gravel Stone Seal",          33, 12, 90, 20, 1.9, "Lightning Spear",           54,  4200),
    Weapon("Dragon Communion Seal",      35, 11, 91, 22, 2.0, "Dragon Maw",                60,  5200),
    Weapon("Erdtree Seal",               37, 10, 93, 24, 2.0, "Triple Rings of Light",     64,  5800),

    # ----- Tier 3: Late game (Areas 6-9, cost 7000-12000) --------------------
    Weapon("Halo Scythe",                40, 12, 85, 20, 1.9, "Miquella's Ring of Light",  68,  7000),
    Weapon("Sword of Night and Flame",   41, 10, 83, 18, 1.9, "Night-and-Flame Stance",    70,  8000),
    Weapon("Marais Executioner's Sword", 43,  7, 77, 16, 2.0, "Eochaid's Dancing Blade",   74,  9000),
    Weapon("Dragon King's Cragblade",    44,  9, 81, 18, 2.0, "Thundercloud Form",         76, 10000),
    Weapon("Cipher Pata",                42, 19, 95, 28, 1.9, "Unblockable Blade",         72, 10000),
    Weapon("Blasphemous Blade",          45,  8, 78, 16, 2.0, "Taker's Flames",            78, 11000),
    Weapon("Dark Moon Greatsword",       46,  7, 82, 20, 2.0, "Moonlight Greatblade",      80, 12000),
    # -- Sorcery / Incantation staves & seals (Tier 3) -------------------------
    Weapon("Lusat's Glintstone Staff",   43,  9, 98, 28, 2.2, "Stars of Ruin",             76,  7500),
    Weapon("Azur's Glintstone Staff",    41, 10, 98, 26, 2.2, "Comet Azur",                74,  7000),
    Weapon("Prince of Death's Staff",    42,  9, 95, 25, 2.1, "Aspect of the Crucible",    72,  8500),
    Weapon("Giant's Seal",               44,  8, 92, 24, 2.0, "Giant's Flame Take Thee",   78,  9500),
    Weapon("Frenzied Flame Seal",        45,  9, 93, 26, 2.1, "Frenzied Burst",            80, 11500),

    # ----- Tier 4: Endgame (Areas 10-13, cost 13000-18000) -------------------
    Weapon("Royal Greatsword",           48,  6, 76, 18, 2.1, "Wolf's Assault",            84, 13000),
    Weapon("Ghiza's Wheel",              50,  4, 72, 14, 2.1, "Spinning Wheel",            88, 14000),
    Weapon("Starscourge Greatsword",     52,  5, 75, 16, 2.2, "Starcaller Cry",            92, 15000),
    Weapon("Grafted Blade Greatsword",   54,  3, 70, 12, 2.2, "Oath of Vengeance",         96, 16000),
    Weapon("Ruins Greatsword",           55,  4, 73, 14, 2.3, "Wave of Destruction",      100, 17000),
    Weapon("Malenia's Hand",             55, 13, 90, 28, 2.4, "Waterfowl Dance",          100, 18000),
    # -- Sorcery / Incantation staves & seals (Tier 4) -------------------------
    Weapon("Staff of the Avatar",        50,  7, 97, 28, 2.3, "Rotten Breath",             90, 13500),
    Weapon("Dragon Communion Seal+",     52,  8, 96, 30, 2.3, "Ekzykes's Decay",           94, 15500),
    Weapon("Gravel Stone Seal+",         53,  7, 95, 28, 2.3, "Lansseax's Glaive",         96, 16500),
    Weapon("Erdtree Seal+",              55,  6, 97, 30, 2.4, "Elden Stars",              100, 18000),
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

# Armor sorted by cost — defense scales from 14 to 38, costs from 1500 to 16000.
# Heavy armor has negative speed penalty, light armor trades defense for speed/crit.
armor_storage = [
    # ----- Tier 1: Early game (Areas 1-2, cost 1500-3000) --------------------
    armor("Vagabond Knight Armor", 13,  3,  6, 1.2,  1600),
    armor("Land of Reeds Armor",    9,  6,  9, 1.3,  1500),
    armor("Champion Armor",        11,  1,  5, 1.3,  1700),
    armor("Warrior Armor",          9,  5,  8, 1.3,  1500),
    armor("Prophet Robe",           6,  6,  7, 1.3,  1200),
    armor("Raging Wolf Set",         14,  5, 10, 1.4,  1500),
    armor("Hoslow's Set",            16,  3, 12, 1.5,  2000),
    armor("Royal Remains Armor",     15,  4,  9, 1.4,  2000),
    armor("Black Knife Armor",       13,  8, 16, 1.6,  2500),
    armor("Blaidd's Armor",          18,  2,  8, 1.5,  3000),
    # -- Mage / light robes (Tier 1) ------------------------------------------
    armor("Carian Knight Armor",     12,  7, 14, 1.6,  1800),
    armor("Karolos Glintstone Crown",10,  9, 18, 1.7,  2200),  # sorcerer helm
    armor("Preceptor's Robe",        11,  8, 16, 1.7,  2600),

    # ----- Tier 2: Mid game (Areas 3-6, cost 4000-8000) ----------------------
    armor("Crucible Tree Armor",     22,  0,  8, 1.6,  4000),
    armor("Malenia's Armor",         20,  5, 14, 1.7,  5000),
    armor("Hoslow's Oath Set",       24,  1, 10, 1.6,  6000),
    armor("Radahn's Lion Armor",     28, -2,  6, 1.7,  7000),
    armor("Fingerprint Set",         30, -4,  4, 1.5,  8000),
    # -- Mage / light robes (Tier 2) ------------------------------------------
    armor("Raya Lucarian Robe",      18,  6, 16, 1.8,  4500),
    armor("Spellblade's Traveling Attire", 17, 7, 18, 1.8, 5500),
    armor("Snow Witch Hat",          16,  8, 20, 1.9,  6500),  # Ranni's robe set

    # ----- Tier 3: Late/Endgame (Areas 7-13, cost 10000-16000) ---------------
    armor("Crucible Axe Set",        32, -1,  8, 1.7, 10000),
    armor("Veteran's Armor",         34, -2,  6, 1.7, 12000),
    armor("Elden Lord Armor",        36, -3,  5, 1.8, 14000),
    armor("Bull-Goat Armor",         38, -5,  3, 1.8, 16000),
    # -- Mage / light robes (Tier 3) ------------------------------------------
    armor("Lusat's Glintstone Crown",22,  6, 22, 2.0, 11000),  # boss-tier sorcerer
    armor("Azur's Glintstone Crown", 21,  7, 22, 2.0, 11000),
    armor("Deathbed Robe",           20,  5, 18, 1.9, 10000),  # Fia's set
    armor("Haligtree Crest Helm",    24,  4, 16, 1.9, 13000),  # Miquella's order

    # ----- Class starter sets (cost 0, equipped at game start — not sold) -----
    # These exist so class init code can reference them by name.
    # They do NOT appear in the shop because cost == 0.
]


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
# AREAS — list of dicts driving the story loop
#   Each dict holds:
#     name       — location title printed at the start of each area
#     intro      — narrative text shown before minion fights
#     enemies    — pool of minion names to sample from (must match ENEMY_TYPES keys)
#     boss_intro — narrative text shown right before the boss fight
#     boss       — boss name (must match an ENEMY_TYPES key)
#     rest_text  — narrative text shown after the boss is defeated
AREAS = [
    {
        "name":       "Stormhill Gate (Northern Limgrave)",
        "intro":      "The grace of gold is a distant memory here. \n"
                      "Shadows stretch across the jagged cliffs of Limgrave, where the wind \n"
                      "whistles through the ribs of ancient ruins. It serves as a major choke point guarded by soldiers.\n"
                      "The air is thick with the scent of stagnant rain and the rot of the Shattering. \n",
        
        "enemies":    ["Godrick Soldier", "Exile Soldier"],
        "boss_intro":  "A heavy, omen-filled mist settles upon the road. \n"
            "From the high ramparts, a cloaked figure leaps, the earth shuddering \n"
            "beneath his weight. He unfurls a gnarled wooden staff, his eyes \n"
            "burning with a cold, yellow flame. \n\n"
            "'Foul Tarnished, in search of the Elden Ring. \n"
            "Emboldened by the flame of ambition. \n"
            "Someone must extinguish thy flame.' \n\n"
            "Margit, the Fell Omen, stands between you and the gate...",

        "boss":       "Margit, the Fell Omen",
        "rest_text":    "As the Omen's dust settles, a woman in a dark cloak appears beside the Grace. \n"
            "Melina kneels, her hand extended toward the light. \n\n"
            "'Greetings. I have been watching you. \n"
            "To have faced the Fell Omen and survived... you possess a rare strength. \n"
            "I can take you to a place beyond the reach of the Erdtree's shadow. \n"
            "A gathering place for Tarnished champions, guided by grace.' \n\n"
            "She offers her hand. In an instant, you are transported to the \n"
            "Roundtable Hold. Here, the Two Fingers watch over those who would dare to be Lord.",
    },
    {
        "name":       "Stormveil Castle (Borders of Limgrave and Lirunia)",
        "intro":       "You arrive back at the gate.\n\n"
        "A fortress of jagged stone and screaming winds. \n"
            "The air within these walls is heavy with the scent of stagnant blood \n"
            "and the horrific remains of those 'grafted' to serve a dying lord. \n"
            "Crows with blades for talons and Banished Knights circle the ramparts, watching for \n"
            "Tarnished who dare to tread upon the stones of the Golden Lineage.",
        "enemies":    ["Banished Knight", "Grafted Scion"],
        "boss_intro":   "In a courtyard filled with the corpses of trolls, a giant, \n"
            "many-armed king awaits. He looks upon you with eyes of gold and madness. \n\n"
            "'I am the Lord of all that is Golden. \n"
            "And one day, we shall return together... to our home, bathed in rays of gold.' \n\n"
            "Godrick the Grafted lets out a blood-curdling roar and raises \n"
            "his massive axe. He intends to add your limbs to his tangled collection.",
        "boss":       "Godrick the Grafted",
        "rest_text":   "The Shardbearer has been felled, and the first Great Rune is yours. \n"
            "Melina appears once more as the storm over the castle finally breaks. \n\n"
            "'You have done well. The power of a Great Rune is a heavy burden, \n"
            "but it is the only way to mend the Elden Ring.' \n\n"
            "She offers to escort you back to the Roundtable Hold. \n"
            "Master Hewg awaits your return, his hammer ready to shape your legend \n"
            "from the spoils of the demigod.",
    },
    {
        "name":       "Academy of Raya Lucaria (Center of Lirunia of the Lakes)",
        "intro":       "You return and traverse through Lirunia. Grace guides you towards a\n massive, gothic academy rising from the center of a fog-shrouded lake. \n"
            "This is the seat of the Carian Royals and the masters of sorcery. \n"
            "The scholars here wear stone masks to hide their humanity, peering only \n"
            "at the stars to unravel the mysteries of Glintstone. \n"
            "Inside, the air hums with blue energy, and the floors are cluttered \n"
            "with millions of books that contain secrets too dangerous...",

        "enemies":    ["Glintstone Sorcerer", "Marionette"],
        "boss_intro":   "You enter the Grand Library, a vast room filled with crawling scholars \n"
            "and the eerie singing of children. Floating in a golden amber cocoon \n"
            "is the Queen of the Full Moon. \n\n"
            "'Hush, little culver... I'll soon birth thee anew.' \n\n"
            "Rennala descends, clutching her precious amber egg. She is broken-hearted \n"
            "and lost in a dream of rebirth, but her moon-magic remains as lethal \n"
            "as it was during the height of the Carian wars.",
        "boss":       "Rennala, Queen of the Full Moon",
        "rest_text":      "Rennala is not dead, but defeated. She sits in the library, offering \n"
            "the power of 'Respec' to those who possess a Larval Tear. \n\n"
            "Melina appears in the soft moonlight of the library. \n"
            "'The Queen has lost her will, but the Academy's secrets are now yours. \n"
            "The Erdtree looms closer, yet its thorns remain barred to us. \n"
            "We must seek the capital of Leyndell next.' \n\n"
            "She guides you back to the Roundtable Hold to prepare for the long climb \n"
            "up the Grand Lift of Dectus.",
    },
    {
        "name":       "Redmane Castle (Caelid)",
        "intro":         "Leaving the mist of Liurnia behind, you take a detour into a nightmare. \n"
            "The sky over Caelid is a bruised, bleeding red, and the earth is \n"
            "choked by the pulsing growths of the Scarlet Rot. \n"
            "This was once the site of the greatest battle of the Shattering, \n"
            "where General Radahn and Malenia, Goddess of Rot fought to a standstill. \n"
            "Now, only monstrous, oversized dogs and carrion crows roam the wastes, \n"
            "while Radahn’s remaining soldiers hold a 'festival' of war to give \n"
            "their master the honorable death he was denied.",
        "enemies":    ["Radahn Soldier", "Monstrous Dog"],
        "boss_intro":  "The dunes of the Wailing Dunes shift as a massive, gravity-defying \n"
            "figure looms in the distance. General Radahn, once the mightiest \n"
            "demigod of the Shattering, is now a mindless beast, shriven of his \n"
            "wits by the rot. He howls at the stars he once held in place. \n\n"
            "'I shall provide you with a champion's end, General,' Jerren calls out. \n\n"
            "Radahn lets out a guttural roar, drawing two colossal curved swords \n"
            "imbued with gravity magic. Even in madness, the Starscourge remains \n"
            "the most formidable warrior in the Lands Between.",
        "boss":       "Starscourge Radahn",
        "rest_text":              "With a final, earth-shaking crash, the Starscourge is silenced. \n"
            "As his soul fades, the stars he held in suspension for centuries \n"
            "begin to fall, streaking across the sky in a terrifying display. \n\n"
            "Melina appears in the settling dust of the dunes. \n"
            "'The stars are in motion once more. Fate, long frozen, begins to turn. \n"
            "By defeating Radahn, you have opened the way to the eternal city, Nokron.' \n\n"
            "She brings you back to the Roundtable Hold. Master Hewg looks at you \n"
            "with a new glimmer of respect—you have slain the man who conquered the stars.",
    },
    {
        "name":       "Volcano Manor (Mt. Gelmir)",
        "intro":  "You return back to Liurnia. While roaming the Academy of Raya Lucaria, you encounter \n"
            "a strange, mechanical construct—an Abductor Virgin. Before you can \n"
            "strike, its iron doors swing wide, dragging you into its dark, \n"
            "hollow belly. When the doors finally reopen, the smell of lake water \n"
            "is gone, replaced by sulfur and scorched earth. \n\n"
            "You are in the heart of Mt. Gelmir. Within the nearby manor, Lady Tanith \n"
            "offers a grim choice: join their 'family' in open rebellion against \n"
            "the Erdtree by hunting your own kind, or become fodder for the \n"
            "hungry god that slithers beneath the manor's floorboards.",
        "enemies":    ["Man-Serpent", "Abductor Virgin"],
        "boss_intro":  "You descend into a cavern of roiling magma. A colossal serpent \n"
            "stares you down, its skin twitching with the faces of the warriors \n"
            "it has consumed. As it raises its head, a man’s voice—wet and raspy— \n"
            "echoes from the snake's very throat. \n\n"
            "'Join the Serpent King, as family... Together, we will devour \n"
            "the very gods!' \n\n"
            "Rykard, Lord of Blasphemy, pulls a sword of writhing flesh from \n"
            "the serpent's maw, ready to add you to his eternal collective.",
        "boss":       "Rykard, Lord of Blasphemy",
        "rest_text":  "The Great Serpent lies still, and the blasphemous lord is silenced. \n"
            "The manor's hunt has come to a bloody end. \n\n"
            "Melina appears amidst the cooling lava, her expression solemn. \n"
            "'Rykard walked a path of absolute ruin. To consume one's own \n"
            "ambition... it is a fate worse than death. You were right to \n"
            "extinguish his flame.' \n\n"
            "She transports you back to the Roundtable Hold.\n"
    },
    {
        "name":       "Leyndell, Royal Capital",
        "intro":      "After returning, you travel up to the Grand Lift Dectus. \n"
        "You now stand at the threshold of the Erdtree. \n"
            "Leyndell is a city bathed in eternal gold, yet a haunting silence \n"
            "hangs over its streets. Massive stone dragons and white-clad \n"
            "Oracle Envoys herald a new age, while Leyndell Knights guard \n"
            "the path to the throne with fanatical devotion. \n"
            "As you ascend toward the Erdtree’s roots, a golden projection of\n"
            "the First Elden Lord, Godfrey attacks you but suddenly dissapears after a single blow. \n"
            "Vanquishing the ghost of the first king is the only way to reach \n"
            "the final stairs where the true guardian of the throne awaits.",
        "enemies":    ["Leyndell Knight", "Oracle Envoy"],
        "boss_intro": "At the foot of the Erdtree, a figure emerges from the shadows \n"
            "of the throne. It is a face you recognize—the same Omen who \n"
            "hunted you at the Stormhill Gate, now revealed in his true form. \n\n"
            "'The thrones... stained by my curse. Such shame I cannot bear.' \n\n"
            "Morgott, the Omen King, looks upon the empty thrones of his \n"
            "siblings with a mixture of love and hatred. \n"
            "'Wilful traitors, all. Thy kind are all of a piece. \n"
            "Pillage-emboldened by the flame of ambition!' \n\n"
            "He draws a blade hidden within his cane, his blood boiling \n"
            "with the cursed power he has used to defend the city that loathes him.",
        "boss":       "Morgott, the Omen King",
        "rest_text":  "The Omen King lies defeated, his body turning to ash. \n"
            "But the path forward is barred; the Erdtree has warded itself \n"
            "with impenetrable thorns, rejecting even you. \n\n"
            "Melina appears, her eyes fixed on the burning Erdtree above. \n"
            "'The thorns will not yield. To mend the world, we must commit \n"
            "a cardinal sin. We must find the Flame of Ruin to burn the tree.' \n\n"
            "She grants you the Rold Medallion and takes you back to the \n"
            "Roundtable Hold. Master Hewg looks grim; he knows that the path \n"
            "you now tread leads to the forge of the giants, and the end of an age.",
    },
    {
        "name":       "Mountaintops of the Giants",
        "intro":      "The golden sky of the capital vanishes, replaced by a biting, \n"
            "endless blizzard. You have reached the roof of the world, a land \n"
            "of frozen corpses and ancient, blood-stained snow. \n"
            "This is the graveyard of the Fire Giants, the only race that \n"
            "posed a true threat to the Erdtree. \n"
            "Fire Monks patrol the narrow ridges, guarding the 'forbidden' flame, \n"
            "while massive, multi-fingered creatures—the Fingercreepers— \n"
            "scuttle across the cliffs like nightmare insects.",
        "enemies":    ["Fire Monk", "Troll", "Fingercreeper"],
        "boss_intro": "At the edge of a massive, rusted cauldron, a titan of flesh \n"
            "and flame remains. The last of his kind, the Fire Giant has \n"
            "guarded this forge for an age, his body scarred by the war \n"
            "that ended his people. \n\n"
            "He lets out a roar that shakes the mountain itself, ripping \n"
            "a plate of iron from the earth to serve as a shield. \n"
            "To burn the Erdtree, you must first slay the god of the mountain \n"
            "and claim the spark that lingers within his chest.",
        "boss":       "Fire Giant",
        "rest_text":  "The giant lies still, and the way to the Forge of the Giants is open. \n"
            "You stand at the edge of the massive bowl of flame. \n\n"
            "Melina appears, her gaze fixed on the distant Erdtree. \n"
            "'The time has come. To set the world aright, we must burn that \n"
            "which was thought to be eternal. I will play the part of kindling.' \n\n"
            "She closes her eyes, and as she vanishes, the world begins to \n"
            "crack and fade. You are pulled away into a place beyond time— \n"
            "the crumbling city of Farum Azula. Master Hewg waits one last time \n"
            "in the Hold, sensing that the end of all things is near.",
    },
    {
        "name":       "Crumbling Farum Azula",
        "intro":      "You awaken to the roar of a storm that never ends. \n"
            "Farum Azula is a city suspended in the sky, a swirling vortex of \n"
            "shattered stone and ancient temples. This is a place beyond time, \n"
            "where the ruins of a prehistoric age drift through the clouds. \n"
            "Beastmen howl from the rooftops, guarding the tombs of their \n"
            "long-forgotten lords, while the dreaded Wormfaces wander the \n"
            "lower cliffs, weeping as they spread the blight of Deathroot.",
        "enemies":    ["Beastman of Farum Azula", "Wormface"],
        "boss_intro": "At the end of a grand bridge, a hunched figure in tattered robes \n"
            "stands before a sealed door. He turns, his voice a low, guttural snarl. \n\n"
            "'Witless Tarnished... why covet Destined Death? To bird what is lost?' \n\n"
            "The Beast Clergyman stabs his hand into his chest, pulling forth a \n"
            "blade of pure, black-and-red shadow. The robes fall away to reveal \n"
            "Maliketh, the Black Blade. \n"
            "'O, Death. Become my blade, once more.' \n\n"
            "He leaps into the air, moving with a terrifying, fluid speed. \n"
            "He is the death of the gods themselves, and he will not let you pass.",
        "boss":       "Maliketh, the Black Blade",
        "rest_text":  "The Black Blade is shattered, and Destined Death is finally unleashed. \n"
            "A pillar of crimson fire erupts from the heart of the city, \n"
            "striking the Erdtree across the world. The age of immortality is over. \n\n"
            "Melina's presence lingers in the air like a fading whisper. \n"
            "'It is done. The thorns are burned. The path to the Elden Ring is \n"
            "at last laid bare. Go, and become the Lord you were meant to be.' \n\n"
            "You return to the Roundtable Hold. The building is \n"
            "burning, filled with ash. Master Hewg, his memory failing. \n"
            "The final battle awaits at the Ashen Capital.",
    },
    {
        "name":       "Mohgwyn Palace (Beneath Caelid)",
        "intro":      "While waiting for the fires of Leyndell to settle, you descend \n"
            "into the depths of Nokron the Eternal City. From the starlit ruins of the Siofra \n"
            "River, you find a hidden gateway leading deeper still. \n"
            "You emerge in a blood-soaked mausoleum built into the roots of \n"
            "the world. The air is thick with the scent of copper and old \n"
            "wounds. This is the seat of the Mohgwyn Dynasty, a kingdom built \n"
            "on the promise of a coming age of blood. Red-skinned Albinaurics \n"
            "patrol the crimson swamps, their eyes glazed with fanatical devotion.",
        "enemies":    ["Red Albinauric", "Sanguine Noble"],
        "boss_intro": "At the top of the grand mausoleum, a figure steps out from a pool \n"
            "of bubbling blood. He stands before a massive, withered cocoon \n"
            "containing the stolen Empyrean, Miquella. \n\n"
            "'Dearest Miquella... you must abide alone a while longer.' \n\n"
            "Mohg, the Lord of Blood, turns to you with a trident in hand, \n"
            "his horns curling into his eyes. \n"
            "'Welcome, honored guest, to the birthplace of our Dynasty!' \n\n"
            "He raises his hand to the sky, beginning a rhythmic, cursed chant: \n"
            "'Tres... Duo... Unus... NIHIL!'",
        "boss":       "Mohg, Lord of Blood",
        "rest_text":  "The Lord of Blood has been silenced, and his dreams of a new dynasty \n"
    "are shattered. The cocoon remains still, but the blood-god's influence \n"
    "lingers in the cold stone of the palace. \n\n"
    "The fading guidance of gold beckons from the red twilight. \n"
    "Though the maiden is gone, her purpose echoes through the silence: \n"
    "'Mohg was a creature of obsession, chasing a shadow that would \n"
    "never love him back. But his defeat has cleared a path.' \n\n"
    "You travel back to the Roundtable Hold.",
    },
    {
        "name":       "Miquella's Haligtree",
        "intro":      "You have found the hidden path to the sanctuary of the outcasts. \n"
            "Miquella's Haligtree is a colossal, ivory-white tree that grows \n"
            "within a frozen sea. You descend through its golden branches, \n"
            "passing through the city of Elphael. \n"
            "The air is sweet but sickly, choked by the scent of blooming rot. \n"
            "Cleanrot Knights, the most loyal of Malenia's warriors, guard \n"
            "the path with golden spears, their armor pitted by the very \n"
            "infection they carry for their goddess.",
        "enemies":    ["Cleanrot Knight", "Haligtree Knight"],
        "boss_intro": "At the lowest roots of the tree, a woman sits in a chair of \n"
            "intertwined wood, her prosthetic arm resting on her lap. \n"
            "She rises slowly, her movements graceful despite the rot \n"
            "that has taken her eyes and limbs. \n\n"
            "'I dreamt for so long. My flesh was dull gold... and my blood, rotted. \n"
            "Corpse after corpse, left in my wake. As I awaited his return.' \n\n"
            "She dons her winged helm and unsheathes a blade of singular \n"
            "craftsmanship. \n"
            "'I am Malenia. Blade of Miquella. \n"
            "And I have never known defeat.'",
        "boss":       "Malenia, Blade of Miquella",
        "rest_text":  "The Goddess of Rot has finally met her match. As her form \n"
            "dissolves into a massive, blooming scarlet flower, a heavy \n"
            "silence returns to the roots of the Haligtree. \n\n"
            "The fading guidance of gold flickers weakly in the rot-stained air. \n"
            "A memory of Melina’s sacrifice urges you forward: \n"
            "'You have conquered the greatest of the demigods. No soul \n"
            "left in this world can deny your claim to the throne.' \n\n"
            "You travel back to the Roundtable Hold one last time. \n"
            "The building is nearly ash, and Master Hewg’s hammer falls slow. \n"
            "The path to the Ashen Capital is open. The Elden Ring awaits.",
    },
    {
        "name":       "Leyndell, Ashen Capital",
        "intro":      "You return to Leyndell to proceed your journey.\n The sky is a swirling vortex of embers and soot. \n"
            "Leyndell, once the jewel of the Lands Between, lies buried beneath \n"
            "a mountain of white ash. The Erdtree is a hollow, burning husk, \n"
            "its thorns finally scorched away. \n"
            "Crucible Knights—the ancient warriors who served the first lord— \n"
            "patrol the gray dunes, their golden armor tarnished by the end of \n"
            "an age. You wade through the remains of a civilization to reach \n"
            "the foot of the Elden Throne.",
        "enemies":    ["Crucible Knight", "Erdtree Guardian"],
        "boss_intro": "At the top of the stairs, a massive warrior stands over the dying \n"
            "body of Morgott. He holds his son with a tenderness that defies \n"
            "his savage strength. He turns, a spectral lion ghost perched upon \n"
            "his back to suppress his bloodlust. \n\n"
            "'It has been a long while, Morgott.' \n\n"
            "He looks at you, his eyes recognizing a fellow Tarnished who has \n"
            "made the long journey. \n"
            "'I am Godfrey. First Elden Lord. \n"
            "Alas, I have returned. To be granted audience once more!' \n\n",
        "boss":       "Godfrey / Hoarah Loux",
        "rest_text":  "The First Elden Lord lies defeated, his strength proven inferior\n even after removing the lion suppressing his strength.\n"
            "He smiles in his final moments, acknowledging your \n"
            "right to rule. \n\n"
            "The fading guidance of gold is almost gone now, replaced by the \n"
            "roaring heat of the Erdtree's interior. \n"
            "The memory of Melina’s sacrifice burns brighter than ever: \n"
            "'The path is open. Enter the Erdtree. Forge a new future from \n"
            "the shards of the past.' \n\n"
            "You travel back to the Roundtable Hold one last time to prepare. The blacksmith, Master Hewg, \n"
            "has lost his mind to the forge, but his work is done. \n"
            "You hold a weapon capable of slaying a god. The Elden Ring is within reach.",
    },
   {
        "name": "Inside the Erdtree",
        "intro": 
            "You step through the burning light and into the heart of the tree. \n"
            "Inside, the world is a golden vacuum, where the laws of reality \n"
            "begin to dissolve. There are no soldiers left to fight, only the \n"
            "echoes of a divinity that has failed its own people. \n"
            "You walk toward a suspended figure, a broken vessel that was \n"
            "once both Queen and King.",
        "enemies": [],
        "boss_intro": 
            "The body of Queen Marika falls from its shackles, but as it \n"
            "hits the ground, the hair turns from gold to red. The flesh \n"
            "hardens into stone. A hammer, glowing with the light of the \n"
            "Elden Ring, manifests in his hand. \n\n"
            "Radagon of the Golden Order stands tall, a fractured statue \n"
            "of a god. He does not speak; he only raises his hammer to \n"
            "execute the last will of a dying age. \n"
            "He is the loyal hound of the Greater Will, and he will fight \n"
            "until the last shard of his body is dust.",
        "boss": "Radagon of the Golden Order",
        "rest_text": 
            "Radagon falls, but the struggle for the throne is not over. \n"
            "A pool of liquid shadow spreads across the floor, and the \n"
            "very fabric of the Erdtree begins to shift. \n\n"
            "The memory of the maiden's sacrifice is a silent flame in your soul. \n"
            "'The Greater Will has one final trial for the one who would be Lord. \n"
            "Face the star-born beast. Prove that a Tarnished is master of their own fate.'",
        "final_stretch": True,
    },
    {
        "name": "The Elden Throne",
        "intro": 
            "The golden void expands into an endless, starlit sea. \n"
            "The 'tree' is gone, replaced by a cosmic expanse that stretches \n"
            "into the infinite. You stand upon water that does not ripple, \n"
            "awaiting the true form of the world's master.",
        "enemies": [],
        "boss_intro": 
            "From the dark waters rises a creature of starlight and \n"
            "ancient nebulae. It is the Elden Beast, the vassal of the \n"
            "Greater Will and the living incarnation of the Elden Ring itself. \n\n"
            "It holds a blade forged from the very spine of the god you \n"
            "just defeated. It is not a warrior; it is a force of nature, \n"
            "a cosmic law that refuses to be rewritten. \n"
            "To become Lord, you must kill a god.",
        "boss": "Elden Beast",
        "rest_text": 
            "The Elden Beast dissolves into the stars, and silence finally \n"
            "falls over the Lands Between. You stand before the shattered \n"
            "husk of Marika, the Elden Ring hovering within your reach. \n\n"
            "The choice of an age rests in your hands. \n\n"
            "Will you mend the fractured Ring, claiming the throne to \n"
            "become Elden Lord and bring stability to a broken world? \n\n"
            "Or will you let the yellow flame of madness consume you, \n"
            "becoming the Lord of Frenzied Flame to burn it all away until \n"
            "nothing remains but ash and chaos? \n\n"
            "The Ring is yours. Choose the path of your Order.",
        "ending": True,
    },
]

# Function runesReward(enemy_type)
#   Award runes to hero based on the defeated enemy type
#   Minions give small rune rewards, bosses give large rewards
#   Print the runes earned and hero's new total
def runesReward(enemy_type):
    # PRE:  enemy_type is a string matching a key in monster.ENEMY_TYPES;
    #       hero is a global player object with a runes attribute
    # POST: A random rune amount scaled to the enemy's difficulty is added
    #       to hero.runes; the amount earned and new total are printed

    # ----- Existing Enemies ------------------------------------------------------
    if enemy_type == "Stray Beast":
        earned = random.randint(60, 120)
    elif enemy_type == "Godrick Soldier":
        earned = random.randint(80, 160)
    elif enemy_type == "Carian Sorcerer":
        earned = random.randint(100, 180)
    elif enemy_type == "Vulgar Militiaman":
        earned = random.randint(120, 200)
    elif enemy_type == "Grafted Scion":
        earned = random.randint(150, 260)

    # ----- Stormhill Gate --------------------------------------------------------
    elif enemy_type == "Exile Soldier":
        earned = random.randint(70, 140)

    # ----- Stormveil Castle ------------------------------------------------------
    elif enemy_type == "Banished Knight":
        earned = random.randint(120, 220)

    # ----- Academy of Raya Lucaria -----------------------------------------------
    elif enemy_type == "Glintstone Sorcerer":
        earned = random.randint(160, 280)
    elif enemy_type == "Marionette":
        earned = random.randint(140, 250)

    # ----- Redmane Castle (Caelid) -----------------------------------------------
    elif enemy_type == "Radahn Soldier":
        earned = random.randint(200, 340)
    elif enemy_type == "Monstrous Dog":
        earned = random.randint(180, 300)

    # ----- Volcano Manor ---------------------------------------------------------
    elif enemy_type == "Man-Serpent":
        earned = random.randint(260, 420)
    elif enemy_type == "Abductor Virgin":
        earned = random.randint(300, 480)

    # ----- Leyndell, Royal Capital -----------------------------------------------
    elif enemy_type == "Leyndell Knight":
        earned = random.randint(360, 560)
    elif enemy_type == "Oracle Envoy":
        earned = random.randint(300, 480)

    # ----- Mountaintops of the Giants --------------------------------------------
    elif enemy_type == "Fire Monk":
        earned = random.randint(440, 680)
    elif enemy_type == "Troll":
        earned = random.randint(500, 760)
    elif enemy_type == "Fingercreeper":
        earned = random.randint(400, 620)

    # ----- Mohgwyn Palace --------------------------------------------------------
    elif enemy_type == "Red Albinauric":
        earned = random.randint(500, 760)
    elif enemy_type == "Sanguine Noble":
        earned = random.randint(580, 880)

    # ----- Miquella's Haligtree --------------------------------------------------
    elif enemy_type == "Cleanrot Knight":
        earned = random.randint(660, 980)
    elif enemy_type == "Haligtree Knight":
        earned = random.randint(620, 940)

    # ----- Crumbling Farum Azula -------------------------------------------------
    elif enemy_type == "Beastman of Farum Azula":
        earned = random.randint(740, 1100)
    elif enemy_type == "Wormface":
        earned = random.randint(680, 1020)

    # ----- Leyndell, Ashen Capital -----------------------------------------------
    elif enemy_type == "Crucible Knight":
        earned = random.randint(820, 1220)
    elif enemy_type == "Erdtree Guardian":
        earned = random.randint(760, 1140)

    # ----- Bosses ----------------------------------------------------------------
    elif enemy_type == "Margit, the Fell Omen":
        earned = random.randint(800,  1400)
    elif enemy_type == "Godrick the Grafted":
        earned = random.randint(1400, 2200)
    elif enemy_type == "Rennala, Queen of the Full Moon":
        earned = random.randint(2000, 3200)
    elif enemy_type == "Starscourge Radahn":
        earned = random.randint(3000, 4600)
    elif enemy_type == "Rykard, Lord of Blasphemy":
        earned = random.randint(4000, 6000)
    elif enemy_type == "Morgott, the Omen King":
        earned = random.randint(5200, 7600)
    elif enemy_type == "Fire Giant":
        earned = random.randint(6400, 9200)
    elif enemy_type == "Mohg, Lord of Blood":
        earned = random.randint(7800, 11000)
    elif enemy_type == "Malenia, Blade of Miquella":
        earned = random.randint(9200, 13000)
    elif enemy_type == "Maliketh, the Black Blade":
        earned = random.randint(10600, 14800)
    elif enemy_type == "Godfrey / Hoarah Loux":
        earned = random.randint(12000, 16400)
    elif enemy_type == "Radagon of the Golden Order":
        earned = random.randint(13600, 18200)
    elif enemy_type == "Elden Beast":
        earned = random.randint(15200, 20000)

    else:
        earned = 0
        print(f"WARNING: No rune reward defined for '{enemy_type}'")

    hero.runes += earned
    print(f"\nYou gained {earned} runes!")
    print(f"Total runes: {hero.runes}")

# Function shop()
#   Loop forever (until player chooses "leave")
#     Clear the screen and print the shop header with hero's current rune count
#     Prompt the player for a choice: "weapon", "armor", "flask", or "leave"
#     If choice is "weapon": show weapons, prompt name, buy if affordable
#     If choice is "armor": show armor, prompt name, buy if affordable
#     If choice is "flask": show flask cost (200 runes each, max 12),
#       buy one flask charge if affordable and not already at max
#     If choice is "leave": break
#     Else: print error
def shop():
    # PRE:  hero is a global player object with runes attribute;
    #       weapon_storage, armor_storage are non-empty lists;
    #       heal_stash[0] is the player's flask object;
    #       equipped_armor is a global armor object that can be reassigned
    # POST: Player buys items until they choose "leave";
    #       runes decremented accordingly; equipped_armor or stash updated
    global equipped_armor
    while True:
        clear()
        print("=" * 40)
        print("       THE ROUNDTABLE HOLD")
        print("=" * 40)
        print(f"Runes held: {hero.runes}")
        print(f"Flasks:     {heal_stash[0].heal_quantity}/12")
        print("\nHewg hammers away at a blunt blade, the rhythm echoing through the hall.")

        choice = input(
            '\nSmithing Master Hewg: "Lay out your arms... Offer up thy runes, and let us strike a bargain..."\n'
            "(weapon / armor / flask / leave): "
        ).strip().lower()

        if choice == "weapon":
            print("\nWeapons available:")
            for w in weapon_storage:
                if w.cost == 0:
                    continue
                print(f"  {w.name} — ATK: {w.attack_power}  SPD: {w.speed}  Cost: {w.cost} runes")
            weapon_choice = input("Which weapon? (or 'cancel'): ").strip()
            if weapon_choice.lower() == "cancel":
                continue
            match = next((w for w in weapon_storage if w.name.lower() == weapon_choice.lower() and w.cost > 0), None)
            if match is None:
                print("Weapon not found.")
            elif hero.runes < match.cost:
                print(f"Not enough runes! You need {match.cost} but have {hero.runes}.")
            else:
                hero.runes -= match.cost
                weapon_stash.append(match)
                print(f"You bought {match.name}! Runes remaining: {hero.runes}")
            delay(3)

        elif choice == "armor":
            print("\nArmor available:")
            for a in armor_storage:
                if a.cost == 0:
                    continue
                print(f"  {a.name} — DEF: {a.defense}  SPD: {a.speed}  Cost: {a.cost} runes")
            armor_choice = input("Which armor? (or 'cancel'): ").strip()
            if armor_choice.lower() == "cancel":
                continue
            match = next((a for a in armor_storage if a.name.lower() == armor_choice.lower() and a.cost > 0), None)
            if match is None:
                print("Armor not found.")
            elif hero.runes < match.cost:
                print(f"Not enough runes! You need {match.cost} but have {hero.runes}.")
            else:
                hero.runes -= match.cost
                equipped_armor = match
                print(f"You equipped {match.name}! Runes remaining: {hero.runes}")
            delay(3)

        elif choice == "flask":
            flask = heal_stash[0]
            flask_cost = 200
            if flask.heal_quantity >= 12:
                print(f"\nYour flasks are already full! ({flask.heal_quantity}/12)")
            elif hero.runes < flask_cost:
                print(f"\nNot enough runes! A flask charge costs {flask_cost} runes.")
            else:
                hero.runes -= flask_cost
                flask.heal_quantity += 1
                print(f"\nFlask refilled! ({flask.heal_quantity}/12)  Runes remaining: {hero.runes}")
            delay(3)

        elif choice == "leave":
            break
        else:
            print("Please choose 'weapon', 'armor', 'flask', or 'leave'.")


# Class monster
#   ENEMY_TYPES — dictionary mapping enemy name strings to their stat dictionaries
#
#   Constructor __init__(enemy_type=None)
#     If enemy_type is None, randomly pick one key from ENEMY_TYPES
#     Look up the stat dictionary for that enemy_type
#     Store all stats (health, attack_power, defense, speed, accuracy,
#     crit_chance, crit_damage, special_attack, special_attack_damage)
#     as attributes; set max_health equal to the starting health value
#
#   Method attack(target)
#     Roll a random number between 1 and 100
#     If the roll is greater than self.accuracy, print "missed!" and return True
#     Set damage to self.attack_power
#     Roll for a critical hit; if the roll <= crit_chance, multiply damage by crit_damage
#     Calculate total_defense as target.defense + equipped_armor.defenseA
#     Subtract total_defense from damage (floor at 1)
#     Subtract damage from target.health (floor at 0)
#     Print damage dealt and target's remaining HP; return True
#
#   Method special(target)
#     Print the special attack name
#     Set damage to self.special_attack_damage
#     Calculate total_defense as target.defense + equipped_armor.defense
#     Subtract total_defense from damage (floor at 1)
#     Subtract damage from target.health (floor at 0)
#     Print damage dealt and target's remaining HP; return True

class monster:
    # PRE:  enemy_type is either None or a string key that exists in ENEMY_TYPES;
    #       if None, a random enemy type is selected
    # POST: A monster object is created with all stats loaded from ENEMY_TYPES
    #       for the chosen type; health and max_health are both set to the
    #       starting health value
    ENEMY_TYPES = {
    # ----- Legacy / Intro enemies ---------------------------------------------
    "Stray Beast": {
        "health": 40, "attack_power": 8, "defense": 2,
        "speed": 20, "accuracy": 82, "crit_chance": 8,
        "crit_damage": 1.4, "special_attack": "Rabid Lunge",
        "special_attack_damage": 16
    },
    "Godrick Soldier": {
        "health": 45, "attack_power": 12, "defense": 6,
        "speed": 8, "accuracy": 74, "crit_chance": 5,
        "crit_damage": 1.5, "special_attack": "Shield Bash",
        "special_attack_damage": 20
    },
    "Carian Sorcerer": {
        "health": 40, "attack_power": 14, "defense": 3,
        "speed": 12, "accuracy": 88, "crit_chance": 12,
        "crit_damage": 1.5, "special_attack": "Glintstone Pebble",
        "special_attack_damage": 24
    },
    "Vulgar Militiaman": {
        "health": 50, "attack_power": 16, "defense": 4,
        "speed": 16, "accuracy": 78, "crit_chance": 16,
        "crit_damage": 1.7, "special_attack": "Beast Claw",
        "special_attack_damage": 28
    },
    "Grafted Scion": {
        "health": 55, "attack_power": 18, "defense": 8,
        "speed": 14, "accuracy": 74, "crit_chance": 14,
        "crit_damage": 1.8, "special_attack": "Unending Flurry",
        "special_attack_damage": 32
    },

    # ----- Stormhill Gate (Area 1) -------------------------------------------
    "Exile Soldier": {
        "health": 42, "attack_power": 10, "defense": 5,
        "speed": 10, "accuracy": 74, "crit_chance": 5,
        "crit_damage": 1.4, "special_attack": "Desperate Slash",
        "special_attack_damage": 18
    },

    # ----- Stormveil Castle (Area 2) -----------------------------------------
    "Banished Knight": {
        "health": 55, "attack_power": 14, "defense": 8,
        "speed": 9, "accuracy": 76, "crit_chance": 7,
        "crit_damage": 1.5, "special_attack": "Charged Thrust",
        "special_attack_damage": 24
    },

    # ----- Academy of Raya Lucaria (Area 3) ----------------------------------
    "Glintstone Sorcerer": {
        "health": 50, "attack_power": 18, "defense": 4,
        "speed": 13, "accuracy": 86, "crit_chance": 15,
        "crit_damage": 1.6, "special_attack": "Glintstone Arc",
        "special_attack_damage": 30
    },
    "Marionette": {
        "health": 52, "attack_power": 14, "defense": 5,
        "speed": 15, "accuracy": 80, "crit_chance": 9,
        "crit_damage": 1.5, "special_attack": "Arrow Volley",
        "special_attack_damage": 24
    },

    # ----- Redmane Castle / Caelid (Area 4) ----------------------------------
    "Radahn Soldier": {
        "health": 58, "attack_power": 20, "defense": 8,
        "speed": 9, "accuracy": 74, "crit_chance": 6,
        "crit_damage": 1.5, "special_attack": "Scarlet Slash",
        "special_attack_damage": 34
    },
    "Monstrous Dog": {
        "health": 45, "attack_power": 22, "defense": 3,
        "speed": 22, "accuracy": 84, "crit_chance": 12,
        "crit_damage": 1.6, "special_attack": "Rabid Bite",
        "special_attack_damage": 36
    },

    # ----- Volcano Manor (Area 5) --------------------------------------------
    "Man-Serpent": {
        "health": 62, "attack_power": 24, "defense": 7,
        "speed": 11, "accuracy": 78, "crit_chance": 10,
        "crit_damage": 1.6, "special_attack": "Venom Fang",
        "special_attack_damage": 40
    },
    "Abductor Virgin": {
        "health": 70, "attack_power": 26, "defense": 12,
        "speed": 7, "accuracy": 70, "crit_chance": 7,
        "crit_damage": 1.7, "special_attack": "Iron Maiden Crush",
        "special_attack_damage": 44
    },

    # ----- Leyndell, Royal Capital (Area 6) ----------------------------------
    "Leyndell Knight": {
        "health": 68, "attack_power": 28, "defense": 13,
        "speed": 10, "accuracy": 78, "crit_chance": 9,
        "crit_damage": 1.7, "special_attack": "Golden Vow Strike",
        "special_attack_damage": 46
    },
    "Oracle Envoy": {
        "health": 55, "attack_power": 24, "defense": 5,
        "speed": 8, "accuracy": 82, "crit_chance": 7,
        "crit_damage": 1.5, "special_attack": "Bubble Burst",
        "special_attack_damage": 40
    },

    # ----- Mountaintops of the Giants (Area 7) -------------------------------
    "Fire Monk": {
        "health": 72, "attack_power": 30, "defense": 9,
        "speed": 10, "accuracy": 76, "crit_chance": 9,
        "crit_damage": 1.7, "special_attack": "Flame Surge",
        "special_attack_damage": 50
    },
    "Troll": {
        "health": 90, "attack_power": 32, "defense": 12,
        "speed": 5, "accuracy": 62, "crit_chance": 5,
        "crit_damage": 2.0, "special_attack": "Boulder Slam",
        "special_attack_damage": 54
    },
    "Fingercreeper": {
        "health": 60, "attack_power": 28, "defense": 5,
        "speed": 18, "accuracy": 80, "crit_chance": 14,
        "crit_damage": 1.6, "special_attack": "Grasp",
        "special_attack_damage": 46
    },

    # ----- Mohgwyn Palace (Area 8) -------------------------------------------
    "Red Albinauric": {
        "health": 60, "attack_power": 28, "defense": 5,
        "speed": 14, "accuracy": 78, "crit_chance": 10,
        "crit_damage": 1.6, "special_attack": "Blood Surge",
        "special_attack_damage": 46
    },
    "Sanguine Noble": {
        "health": 70, "attack_power": 32, "defense": 8,
        "speed": 12, "accuracy": 81, "crit_chance": 16,
        "crit_damage": 1.8, "special_attack": "Bloodflame Ritual",
        "special_attack_damage": 52
    },

    # ----- Miquella's Haligtree (Area 9) -------------------------------------
    "Cleanrot Knight": {
        "health": 78, "attack_power": 34, "defense": 15,
        "speed": 11, "accuracy": 79, "crit_chance": 11,
        "crit_damage": 1.8, "special_attack": "Rot Spear Thrust",
        "special_attack_damage": 56
    },
    "Haligtree Knight": {
        "health": 75, "attack_power": 32, "defense": 14,
        "speed": 10, "accuracy": 77, "crit_chance": 9,
        "crit_damage": 1.7, "special_attack": "Sacred Blade",
        "special_attack_damage": 52
    },

    # ----- Crumbling Farum Azula (Area 10) -----------------------------------
    "Beastman of Farum Azula": {
        "health": 80, "attack_power": 36, "defense": 10,
        "speed": 16, "accuracy": 78, "crit_chance": 13,
        "crit_damage": 1.8, "special_attack": "Beast Cleave",
        "special_attack_damage": 58
    },
    "Wormface": {
        "health": 72, "attack_power": 32, "defense": 7,
        "speed": 8, "accuracy": 68, "crit_chance": 7,
        "crit_damage": 1.6, "special_attack": "Death Breath",
        "special_attack_damage": 54
    },

    # ----- Leyndell, Ashen Capital (Area 11) ---------------------------------
    "Crucible Knight": {
        "health": 88, "attack_power": 38, "defense": 18,
        "speed": 9, "accuracy": 75, "crit_chance": 9,
        "crit_damage": 1.9, "special_attack": "Aspects of the Crucible",
        "special_attack_damage": 62
    },
    "Erdtree Guardian": {
        "health": 78, "attack_power": 34, "defense": 12,
        "speed": 12, "accuracy": 78, "crit_chance": 11,
        "crit_damage": 1.7, "special_attack": "Golden Slam",
        "special_attack_damage": 56
    },

    # ----- Bosses (health 200-600, scaling with area) ------------------------
    "Margit, the Fell Omen": {
        "health": 200, "attack_power": 22, "defense": 8,
        "speed": 14, "accuracy": 82, "crit_chance": 14,
        "crit_damage": 1.8, "special_attack": "Holy Blade Barrage",
        "special_attack_damage": 38
    },
    "Godrick the Grafted": {
        "health": 240, "attack_power": 26, "defense": 10,
        "speed": 10, "accuracy": 78, "crit_chance": 12,
        "crit_damage": 1.9, "special_attack": "Dragon Breath Arm",
        "special_attack_damage": 46
    },
    "Rennala, Queen of the Full Moon": {
        "health": 260, "attack_power": 28, "defense": 6,
        "speed": 16, "accuracy": 86, "crit_chance": 18,
        "crit_damage": 1.9, "special_attack": "Full Moon Sorcery",
        "special_attack_damage": 50
    },
    "Starscourge Radahn": {
        "health": 300, "attack_power": 32, "defense": 14,
        "speed": 12, "accuracy": 76, "crit_chance": 12,
        "crit_damage": 2.0, "special_attack": "Meteor Shower",
        "special_attack_damage": 56
    },
    "Rykard, Lord of Blasphemy": {
        "health": 330, "attack_power": 34, "defense": 12,
        "speed": 8, "accuracy": 74, "crit_chance": 10,
        "crit_damage": 2.0, "special_attack": "Serpent's Hunger",
        "special_attack_damage": 60
    },
    "Morgott, the Omen King": {
        "health": 360, "attack_power": 36, "defense": 14,
        "speed": 18, "accuracy": 81, "crit_chance": 16,
        "crit_damage": 2.1, "special_attack": "Cursed Blood Blade",
        "special_attack_damage": 64
    },
    "Fire Giant": {
        "health": 400, "attack_power": 40, "defense": 16,
        "speed": 5, "accuracy": 66, "crit_chance": 8,
        "crit_damage": 2.2, "special_attack": "Flame Crater",
        "special_attack_damage": 70
    },
    "Mohg, Lord of Blood": {
        "health": 420, "attack_power": 42, "defense": 14,
        "speed": 15, "accuracy": 80, "crit_chance": 18,
        "crit_damage": 2.2, "special_attack": "Bloodboon Ritual",
        "special_attack_damage": 74
    },
    "Malenia, Blade of Miquella": {
        "health": 440, "attack_power": 44, "defense": 12,
        "speed": 22, "accuracy": 90, "crit_chance": 24,
        "crit_damage": 2.3, "special_attack": "Waterfowl Dance",
        "special_attack_damage": 78
    },
    "Maliketh, the Black Blade": {
        "health": 460, "attack_power": 46, "defense": 14,
        "speed": 20, "accuracy": 83, "crit_chance": 18,
        "crit_damage": 2.3, "special_attack": "Black Blade Slash",
        "special_attack_damage": 82
    },
    "Godfrey / Hoarah Loux": {
        "health": 480, "attack_power": 46, "defense": 16,
        "speed": 14, "accuracy": 80, "crit_chance": 14,
        "crit_damage": 2.3, "special_attack": "Earthshaker",
        "special_attack_damage": 84
    },
    "Radagon of the Golden Order": {
        "health": 520, "attack_power": 48, "defense": 18,
        "speed": 16, "accuracy": 84, "crit_chance": 18,
        "crit_damage": 2.4, "special_attack": "Elden Stars",
        "special_attack_damage": 88
    },
    "Elden Beast": {
        "health": 580, "attack_power": 50, "defense": 20,
        "speed": 14, "accuracy": 82, "crit_chance": 20,
        "crit_damage": 2.5, "special_attack": "Cosmic Breath",
        "special_attack_damage": 94
    },
    }


    def __init__(self, enemy_type=None):
        if enemy_type is None:
            enemy_type = random.choice(list(self.ENEMY_TYPES.keys()))
        stats = self.ENEMY_TYPES[enemy_type]
        self.name                  = enemy_type
        self.enemy_type            = enemy_type
        self.health                = stats["health"]
        self.max_health            = stats["health"]
        self.attack_power          = stats["attack_power"]
        self.defense               = stats["defense"]
        self.speed                 = stats["speed"]
        self.accuracy              = stats["accuracy"]
        self.crit_chance           = stats["crit_chance"]
        self.crit_damage           = stats["crit_damage"]
        self.special_attack        = stats["special_attack"]
        self.special_attack_damage = stats["special_attack_damage"]

    def attack(self, target):
        # PRE:  target is a player object with health, max_health, and defense
        #       attributes; equipped_armor is a global armor object with a defense
        #       attribute; self.accuracy, crit_chance, and crit_damage are set
        # POST: A hit-chance roll is made against self.accuracy;
        #       if the attack misses, a miss message is printed and True is returned;
        #       if the attack hits, damage is calculated (with possible crit),
        #       reduced by (target.defense + equipped_armor.defense), floored at 1,
        #       and target.health is reduced accordingly (floored at 0);
        #       damage dealt and target's remaining HP are printed; returns True
        hit_chance = random.randint(1, 100)
        if hit_chance > self.accuracy:
            print(f"{self.name}'s attack missed!")
            return True

        damage = self.attack_power
        crit_roll = random.randint(1, 100)
        if crit_roll <= self.crit_chance:
            damage = int(damage * self.crit_damage)
            print("CRITICAL HIT!")

        total_defense = target.defense + equipped_armor.defense
        damage = max(1, damage - total_defense)

        target.health -= damage
        if target.health < 0:
            target.health = 0

        print(f"{self.name} attacks {target.name} for {damage} damage!")
        print(f"{target.name} has {target.health}/{target.max_health} HP left.")
        return True

    def special(self, target):
        # PRE:  target is a player object with health, max_health, and defense
        #       attributes; equipped_armor is a global armor object with a defense
        #       attribute; self.special_attack and self.special_attack_damage are set
        # POST: self.special_attack_damage is reduced by total defense (floored at 1),
        #       target.health is reduced by that amount (floored at 0);
        #       the special attack name, damage dealt, and target's remaining HP
        #       are printed; returns True
        print(f"{self.name} uses {self.special_attack}!")
        damage = int(self.special_attack_damage)
        total_defense = target.defense + equipped_armor.defense
        damage = max(1, damage - total_defense)
        target.health -= damage
        if target.health < 0:
            target.health = 0
        print(f"{self.special_attack} deals {damage} damage to {target.name}!")
        print(f"\n{target.name} has {target.health}/{target.max_health} HP left.")
        return True


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


# ----- battle_loop -----------------------------------------------------------
# Function battle_loop(enemy)
#   Determine who goes first: hero goes first if hero.speed >= enemy.speed
#   While hero.health > 0 AND enemy.health > 0
#     Delay 8 seconds, clear the screen, print battle stats
#     If hero's turn: tick cooldowns, loop until valid action, set hero_turn False
#     Else: enemy attacks or uses special, set hero_turn True
#   Clear screen
#   If hero.health <= 0: print defeat, return False
#   Else: print victory, award runes, delay, return True
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
def story_loop():
    # PRE:  hero, heal_stash, equipped_armor, AREAS are all initialized globals;
    #       hero.health > 0 at the start of the call
    # POST: Steps the player through all areas in AREAS in order;
    #       ends early if hero dies; calls ending_choice() on the final area
    for area in AREAS:

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
                enemy = monster(enemy_type)
                if not battle_loop(enemy):
                    return

        # ----- 3. Boss intro -------------------------------------------------
        prompt(area["boss_intro"])
        input("\nPress Enter to continue...")

        # ----- 4. Boss fight -------------------------------------------------
        boss = monster(area["boss"])
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
            input("\nPress Enter to continue...")
        else:
            prompt(area["rest_text"])
            hero.health = hero.max_health
            input("\nPress Enter to continue...")
            shop()


# ── Character creation ─────────────────────────────────────────
# Character Creation
#   Clear the screen
#   Loop until the player enters a valid name (non-empty, letters/spaces only)
#   Loop until the player enters a valid class choice (1-8)
#   Build hero, weapon_stash, and equipped_armor based on class choice
#   Print a welcome message displaying the hero's starting stats
#   Set fight to False
clear()

# ----- Name validation -------------------------------------------------------
while True:
    player_name = input("What is your name, Tarnished? ").strip()
    if not player_name:
        print("You must enter a name to continue.")
    elif not all(c.isalpha() or c.isspace() for c in player_name):
        print("Name must contain only letters and spaces.")
    else:
        break

# ----- Class selection -------------------------------------------------------
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


# Story Introduction Loop
#   Loop forever
#     Print the story intro text and prompt the player to choose "left" or "right"
#     If the player chooses "left"
#       Clear the screen and print the left-path narrative
#       Set fight to True and break out of the loop
#     Else if the player chooses "right"
#       Clear the screen and print the right-path narrative
#       Set fight to True and break out of the loop
#     Else
#       Print a message asking the player to choose left or right
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
if fight:
    delay(2)
    intro_enemy = monster("Grafted Scion")
    survived = battle_loop(intro_enemy)
    if survived:
        prompt(
            "The Grafted Scion crumbles.\n"
            "Grace guides you forward. The road to the Erdtree begins. You are now in the Lands of Between.\n"
        )
        delay(6)
        story_loop()