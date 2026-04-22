# Elden Ring Turn Based Game - Storyline Data
# Contains enemies, areas, shop items, and related functions

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
    "health": 60, "attack_power": 20, "defense": 10,
    "speed": 6, "accuracy": 70, "crit_chance": 10,
    "crit_damage": 1.6, "special_attack": "Charge Attack",
    "special_attack_damage": 36
},
# ----- Academy of Raya Lucaria (Area 3) -----------------------------------
"Glintstone Sorcerer": {
    "health": 50, "attack_power": 18, "defense": 4,
    "speed": 14, "accuracy": 90, "crit_chance": 15,
    "crit_damage": 1.6, "special_attack": "Glintstone Arc",
    "special_attack_damage": 30
},
"Marionette": {
    "health": 48, "attack_power": 16, "defense": 6,
    "speed": 18, "accuracy": 80, "crit_chance": 12,
    "crit_damage": 1.5, "special_attack": "Puppet Strings",
    "special_attack_damage": 28
},
# ----- Redmane Castle (Caelid) (Area 4) -----------------------------------
"Radahn Soldier": {
    "health": 65, "attack_power": 22, "defense": 8,
    "speed": 12, "accuracy": 75, "crit_chance": 12,
    "crit_damage": 1.7, "special_attack": "Lance Charge",
    "special_attack_damage": 38
},
"Monstrous Dog": {
    "health": 55, "attack_power": 19, "defense": 5,
    "speed": 20, "accuracy": 78, "crit_chance": 18,
    "crit_damage": 1.8, "special_attack": "Bite",
    "special_attack_damage": 34
},
# ----- Volcano Manor (Mt. Gelmir) (Area 5) --------------------------------
"Man-Serpent": {
    "health": 70, "attack_power": 24, "defense": 9,
    "speed": 10, "accuracy": 76, "crit_chance": 14,
    "crit_damage": 1.8, "special_attack": "Serpent Bite",
    "special_attack_damage": 42
},
"Abductor Virgin": {
    "health": 75, "attack_power": 26, "defense": 11,
    "speed": 8, "accuracy": 72, "crit_chance": 16,
    "crit_damage": 1.9, "special_attack": "Abduction",
    "special_attack_damage": 46
},
# ----- Leyndell, Royal Capital (Area 6) -----------------------------------
"Leyndell Knight": {
    "health": 80, "attack_power": 28, "defense": 12,
    "speed": 8, "accuracy": 74, "crit_chance": 10,
    "crit_damage": 1.7, "special_attack": "Royal Slash",
    "special_attack_damage": 48
},
"Oracle Envoy": {
    "health": 70, "attack_power": 25, "defense": 7,
    "speed": 15, "accuracy": 85, "crit_chance": 20,
    "crit_damage": 2.0, "special_attack": "Oracle Bubble",
    "special_attack_damage": 44
},
# ----- Mountaintops of the Giants (Area 7) --------------------------------
"Fire Monk": {
    "health": 85, "attack_power": 30, "defense": 10,
    "speed": 12, "accuracy": 76, "crit_chance": 15,
    "crit_damage": 1.8, "special_attack": "Flame Strike",
    "special_attack_damage": 52
},
"Troll": {
    "health": 90, "attack_power": 32, "defense": 14,
    "speed": 6, "accuracy": 70, "crit_chance": 8,
    "crit_damage": 1.6, "special_attack": "Rock Throw",
    "special_attack_damage": 56
},
"Fingercreeper": {
    "health": 78, "attack_power": 27, "defense": 8,
    "speed": 16, "accuracy": 78, "crit_chance": 18,
    "crit_damage": 1.9, "special_attack": "Finger Snap",
    "special_attack_damage": 48
},
# ----- Mohgwyn Palace (Beneath Caelid) (Area 8) ---------------------------
"Red Albinauric": {
    "health": 88, "attack_power": 29, "defense": 11,
    "speed": 14, "accuracy": 80, "crit_chance": 16,
    "crit_damage": 1.9, "special_attack": "Blood Slash",
    "special_attack_damage": 50
},
"Sanguine Noble": {
    "health": 82, "attack_power": 28, "defense": 9,
    "speed": 18, "accuracy": 82, "crit_chance": 22,
    "crit_damage": 2.1, "special_attack": "Blood Spray",
    "special_attack_damage": 50
},
# ----- Miquella's Haligtree (Area 9) --------------------------------------
"Cleanrot Knight": {
    "health": 95, "attack_power": 33, "defense": 13,
    "speed": 10, "accuracy": 75, "crit_chance": 12,
    "crit_damage": 1.8, "special_attack": "Rot Slash",
    "special_attack_damage": 58
},
"Haligtree Knight": {
    "health": 100, "attack_power": 35, "defense": 15,
    "speed": 8, "accuracy": 73, "crit_chance": 10,
    "crit_damage": 1.7, "special_attack": "Haligtree Strike",
    "special_attack_damage": 62
},
# ----- Crumbling Farum Azula (Area 10) ------------------------------------
"Beastman of Farum Azula": {
    "health": 105, "attack_power": 37, "defense": 14,
    "speed": 12, "accuracy": 76, "crit_chance": 14,
    "crit_damage": 1.9, "special_attack": "Beast Roar",
    "special_attack_damage": 66
},
"Wormface": {
    "health": 98, "attack_power": 34, "defense": 12,
    "speed": 16, "accuracy": 78, "crit_chance": 18,
    "crit_damage": 2.0, "special_attack": "Worm Bite",
    "special_attack_damage": 60
},
# ----- Leyndell, Ashen Capital (Area 11) ----------------------------------
"Crucible Knight": {
    "health": 110, "attack_power": 39, "defense": 16,
    "speed": 9, "accuracy": 74, "crit_chance": 12,
    "crit_damage": 1.8, "special_attack": "Crucible Blast",
    "special_attack_damage": 70
},
"Erdtree Guardian": {
    "health": 115, "attack_power": 41, "defense": 18,
    "speed": 7, "accuracy": 72, "crit_chance": 10,
    "crit_damage": 1.7, "special_attack": "Erdtree Beam",
    "special_attack_damage": 74
},
# ----- Bosses ------------------------------------------------------------
"Margit, the Fell Omen": {
    "health": 800, "attack_power": 40, "defense": 20,
    "speed": 25, "accuracy": 90, "crit_chance": 10,
    "crit_damage": 2.0, "special_attack": "Hammer Slam",
    "special_attack_damage": 80
},
"Godrick the Grafted": {
    "health": 1200, "attack_power": 50, "defense": 25,
    "speed": 20, "accuracy": 85, "crit_chance": 15,
    "crit_damage": 2.2, "special_attack": "Grafted Dragon",
    "special_attack_damage": 100
},
"Rennala, Queen of the Full Moon": {
    "health": 1600, "attack_power": 60, "defense": 30,
    "speed": 15, "accuracy": 95, "crit_chance": 20,
    "crit_damage": 2.5, "special_attack": "Full Moon",
    "special_attack_damage": 120
},
"Starscourge Radahn": {
    "health": 2000, "attack_power": 70, "defense": 35,
    "speed": 10, "accuracy": 80, "crit_chance": 25,
    "crit_damage": 2.8, "special_attack": "Gravity Slam",
    "special_attack_damage": 140
},
"Rykard, Lord of Blasphemy": {
    "health": 2400, "attack_power": 80, "defense": 40,
    "speed": 5, "accuracy": 75, "crit_chance": 30,
    "crit_damage": 3.0, "special_attack": "Blasphemous Blade",
    "special_attack_damage": 160
},
"Morgott, the Omen King": {
    "health": 2800, "attack_power": 90, "defense": 45,
    "speed": 0, "accuracy": 70, "crit_chance": 35,
    "crit_damage": 3.2, "special_attack": "Omen Smash",
    "special_attack_damage": 180
},
"Fire Giant": {
    "health": 3200, "attack_power": 100, "defense": 50,
    "speed": -5, "accuracy": 65, "crit_chance": 40,
    "crit_damage": 3.5, "special_attack": "Flame Crater",
    "special_attack_damage": 200
},
"Mohg, Lord of Blood": {
    "health": 3600, "attack_power": 110, "defense": 55,
    "speed": -10, "accuracy": 60, "crit_chance": 45,
    "crit_damage": 3.8, "special_attack": "Bloodboon Ritual",
    "special_attack_damage": 220
},
"Malenia, Blade of Miquella": {
    "health": 4000, "attack_power": 120, "defense": 60,
    "speed": -15, "accuracy": 55, "crit_chance": 50,
    "crit_damage": 4.0, "special_attack": "Waterfowl Dance",
    "special_attack_damage": 240
},
"Maliketh, the Black Blade": {
    "health": 4400, "attack_power": 130, "defense": 65,
    "speed": -20, "accuracy": 50, "crit_chance": 55,
    "crit_damage": 4.2, "special_attack": "Black Blade",
    "special_attack_damage": 260
},
"Godfrey / Hoarah Loux": {
    "health": 4800, "attack_power": 140, "defense": 70,
    "speed": -25, "accuracy": 45, "crit_chance": 60,
    "crit_damage": 4.5, "special_attack": "Hoarah Loux",
    "special_attack_damage": 280
},
"Radagon of the Golden Order": {
    "health": 5200, "attack_power": 150, "defense": 75,
    "speed": -30, "accuracy": 40, "crit_chance": 65,
    "crit_damage": 4.8, "special_attack": "Elden Stars",
    "special_attack_damage": 300
},
"Elden Beast": {
    "health": 5600, "attack_power": 160, "defense": 80,
    "speed": -35, "accuracy": 35, "crit_chance": 70,
    "crit_damage": 5.0, "special_attack": "Cosmic Breath",
    "special_attack_damage": 320
}
}

# Class Weapon
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

# Class armor
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

# Class Heal
class Heal:
    # PRE:  heal_name is a string; heal_amount is a positive int;
    #       heal_quantity is a non-negative int
    # POST: A Heal object is created with the given name, heal amount,
    #       and remaining quantity stored as attributes
    def __init__(self, heal_name, heal_amount, heal_quantity):
        self.heal_name = heal_name
        self.heal_amount = heal_amount
        self.heal_quantity = heal_quantity

# Class monster (moved from main.py)
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
    }

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

        # Assuming equipped_armor is global, but since moving, need to adjust
        # For now, assume it's passed or global
        total_defense = target.defense + equipped_armor.defense
        damage -= total_defense
        damage = max(1, damage)
        target.health -= damage
        target.health = max(0, target.health)
        print(f"{self.name} dealt {damage} damage! {target.name} has {target.health}/{target.max_health} HP remaining.")
        return True

    def special(self, target):
        print(f"{self.name} uses {self.special_attack}!")
        damage = self.special_attack_damage
        total_defense = target.defense + equipped_armor.defense
        damage -= total_defense
        damage = max(1, damage)
        target.health -= damage
        target.health = max(0, target.health)
        print(f"{self.name} dealt {damage} damage! {target.name} has {target.health}/{target.max_health} HP remaining.")
        return True

# AREAS — list of dicts driving the story loop
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
        "intro":       "Leaving the mist of Liurnia behind, you traverse through Lirunia. Grace guides you towards a\n massive, gothic academy rising from the center of a fog-shrouded lake. \n"
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
        "intro":         "Leaving the Academy behind, you take a detour into a nightmare. \n"
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
            "She transports you back to the Roundtable Hold.\n",
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
            "Maliketh, the Black Blade. \n\n"
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
            "burning, filled with ash. Master Hewg looks grim; he knows that the end of an age is near.",
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

# Weapon storage
weapon_storage = [
    # ----- Class starter weapons (cost 0, not sold in shop — for reference) ---
    # These are held at start and not listed in the shop.
    # Listed here so the shop can avoid duplicating them.
    Weapon("Longsword", 16, 10, 80, 15, 1.5, "Square Off", 26, 0),
    Weapon("Uchigatana", 18, 14, 86, 18, 1.6, "Unsheathe", 37, 0),
    Weapon("Axe", 22, 7, 75, 10, 1.6, "Barbaric Roar", 36, 0),
    Weapon("Scimitar", 17, 13, 84, 16, 1.6, "Spinning Slash", 28, 0),
    Weapon("Astrologer's Staff", 14, 12, 94, 22, 2.0, "Glintstone Pebble", 28, 0),
    Weapon("Short Spear", 15, 11, 82, 12, 1.5, "Sacred Blade", 26, 0),
    Weapon("Dagger", 13, 18, 92, 28, 1.9, "Quickstep Stab", 24, 0),
    Weapon("Club", 12, 10, 78, 8, 1.4, "Wild Strikes", 20, 0),

    # ----- Tier 1: Early game (Areas 1-2, cost 800-2000) ----------------------
    Weapon("Broadsword", 18, 9, 78, 12, 1.5, "Parry", 30, 800),
    Weapon("Rapier", 16, 15, 88, 20, 1.7, "Impaling Thrust", 28, 1000),
    Weapon("Mace", 20, 8, 76, 10, 1.6, "Heavy Slam", 34, 1200),
    Weapon("Hand Axe", 19, 11, 80, 14, 1.6, "Chop", 32, 900),
    Weapon("Shortbow", 14, 12, 85, 18, 1.8, "Arrow Volley", 24, 1100),
    Weapon("Carian Sword", 17, 13, 90, 22, 1.9, "Carian Phalanx", 30, 1500),
    Weapon("Glintstone Staff", 15, 10, 92, 25, 2.1, "Glintstone Comet", 26, 1600),
    Weapon("Sacred Seal", 16, 12, 84, 16, 1.7, "Urgent Heal", 28, 1300),
    Weapon("Bandit's Curved Sword", 17, 16, 86, 24, 1.8, "Spinning Strikes", 30, 1400),
    Weapon("Great Club", 24, 6, 72, 8, 1.5, "Earthshatter", 40, 1800),

    # ----- Tier 2: Mid game (Areas 3-5, cost 3000-6000) ----------------------
    Weapon("Claymore", 24, 8, 76, 14, 1.6, "Lion's Claw", 40, 3000),
    Weapon("Katana", 22, 14, 84, 20, 1.8, "Quick Draw", 38, 3500),
    Weapon("Warhammer", 28, 5, 70, 10, 1.7, "Seismic Wave", 48, 4000),
    Weapon("Battle Axe", 26, 9, 78, 16, 1.7, "Cleave", 44, 3200),
    Weapon("Longbow", 18, 10, 82, 22, 1.9, "Piercing Shot", 32, 2800),
    Weapon("Carian Greatsword", 25, 11, 88, 26, 2.0, "Carian Greatsword", 42, 4500),
    Weapon("Meteorite Staff", 20, 8, 90, 28, 2.2, "Meteor", 34, 5000),
    Weapon("Golden Order Seal", 22, 10, 86, 20, 1.9, "Radagon's Rings of Light", 38, 4200),
    Weapon("Bloodhound's Fang", 23, 17, 88, 28, 2.0, "Bloodhound's Step", 40, 4800),
    Weapon("Great Mace", 30, 4, 68, 12, 1.8, "Golden Land", 52, 5500),

    # ----- Tier 3: Late game (Areas 6-9, cost 7000-12000) --------------------
    Weapon("Zweihander", 32, 6, 74, 16, 1.8, "Stamp (Upward Cut)", 56, 7000),
    Weapon("Moonlight Greatsword", 30, 12, 86, 24, 2.0, "Transient Moonlight", 52, 8500),
    Weapon("Giant-Crusher", 36, 3, 66, 12, 1.9, "Endure", 64, 9000),
    Weapon("Greataxe", 34, 7, 76, 18, 1.9, "Wild Strikes", 58, 8000),
    Weapon("Greatbow", 24, 8, 80, 26, 2.1, "Barrage", 42, 7500),
    Weapon("Dark Moon Greatsword", 28, 13, 90, 30, 2.2, "Moonlight Vortex", 48, 10000),
    Weapon("Staff of the Guilty", 26, 9, 88, 32, 2.3, "Guilty", 44, 9500),
    Weapon("Dragon Communion Seal", 24, 11, 84, 24, 2.0, "Dragonfire", 40, 8800),
    Weapon("Rivers of Blood", 29, 15, 86, 32, 2.1, "Blood Blade", 50, 9200),
    Weapon("Star Fist", 38, 2, 64, 14, 2.0, "Star Burst", 68, 11000),

    # ----- Tier 4: Endgame (Areas 10-13, cost 13000-18000) -------------------
    Weapon("Requiem Greatsword", 40, 4, 72, 18, 2.0, "Requiem", 72, 13000),
    Weapon("Meteoric Ore Blade", 35, 10, 84, 28, 2.2, "Meteoric Shower", 60, 14000),
    Weapon("Devourer's Scepter", 30, 12, 92, 35, 2.4, "Devourer of Worlds", 52, 15000),
    Weapon("Marika's Hammer", 42, 1, 60, 15, 2.1, "Hammer of Worthiness", 76, 16000),
    Weapon("Sword of Night and Flame", 33, 14, 88, 34, 2.3, "Night-and-Flame Stance", 56, 14500),
    Weapon("Eclipse Shotel", 31, 16, 90, 36, 2.4, "Eclipse", 54, 15500),
    Weapon("Axe of Godrick", 37, 8, 78, 22, 2.1, "I Command Thee, Kneel!", 66, 13500),
    Weapon("Blasphemous Blade", 34, 11, 82, 26, 2.2, "Taker's Flames", 58, 14000),
    Weapon("Moonlight Sword", 32, 13, 86, 30, 2.3, "Moonlight Wave", 54, 15000),
    Weapon("Sacred Relic Sword", 36, 9, 80, 24, 2.1, "Wave of Gold", 64, 16500),
]

# Armor storage
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

# Function runesReward(enemy_type)
#   Award runes to hero based on the defeated enemy type
#   Minions give small rune rewards, bosses give large rewards
#   Print the runes earned and hero's new total
def runesReward(enemy_type):
    import main
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

    # Assuming hero is global
    main.hero.runes += earned
    print(f"\nYou gained {earned} runes!")
    print(f"Total runes: {main.hero.runes}")

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
    import main
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
        print(f"Runes held: {main.hero.runes}")
        print(f"Flasks:     {main.heal_stash[0].heal_quantity}/12")

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
            elif main.hero.runes < match.cost:
                print(f"Not enough runes! You need {match.cost} but have {main.hero.runes}.")
            else:
                main.hero.runes -= match.cost
                main.weapon_stash.append(match)
                print(f"You bought {match.name}! Runes remaining: {main.hero.runes}")
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
            elif main.hero.runes < match.cost:
                print(f"Not enough runes! You need {match.cost} but have {main.hero.runes}.")
            else:
                main.hero.runes -= match.cost
                main.equipped_armor = match
                print(f"You equipped {match.name}! Runes remaining: {main.hero.runes}")
            delay(3)

        elif choice == "flask":
            flask = main.heal_stash[0]
            flask_cost = 200
            if flask.heal_quantity >= 12:
                print(f"\nYour flasks are already full! ({flask.heal_quantity}/12)")
            elif main.hero.runes < flask_cost:
                print(f"\nNot enough runes! A flask charge costs {flask_cost} runes.")
            else:
                main.hero.runes -= flask_cost
                flask.heal_quantity += 1
                print(f"\nFlask refilled! ({flask.heal_quantity}/12)  Runes remaining: {main.hero.runes}")
            delay(3)

        elif choice == "leave":
            break
        else:
            print("Please choose 'weapon', 'armor', 'flask', or 'leave'.")

# Note: Some functions like clear, delay, prompt are not moved as they are utility functions.
# The monster class uses global equipped_armor, so when importing, need to ensure it's available.