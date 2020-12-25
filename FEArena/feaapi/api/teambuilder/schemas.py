"""
file: api/teambuilder/schemas.py

Contains JSON schemas to control the format of input and output
with regards to the teambuilder and static objects, rather than more
dynamic objects such as are found in api/arena/schemas.py
"""

#########################
# Fundamental and Enumerable Types
#########################

weapon_types = [
                "Sword",
                "Lance",
                "Axe",
                "Bow",
                "Gauntlet",
                "Hidden",
                "Tome",
                "Fire",
                "Wind",
                "Thunder",
                "Light",
                "Dark",
                "Anima",
                "Black Magic",
                "White Magic",
                "Staff",
                "Dragonstone",
                "Beast Weapon",
                "Other"
            ]

weapon_rank_subschema = {
    "type": "object",
    "properties": {
        "base": {"type": "number"},
        "max": {"type": "string"}
    }
}

stat_names = ["hp", "str", "mag", "skl", "spd", "luk", "def", "res", "cha", "con", "mov"]

affinities = ['Anima', 'Light', 'Dark', 'Fire', 'Thunder', 'Wind', 'Ice', 'Water', 'Earth', 'Heaven']

class_stat_subschema = {
    "type": "object",
    "properties": {
        "base": {"type": "number"},
        "max": {"type": "number"},
        "growth": {"type": "number"},
    }
}

unit_stat_subschema = {
    "type": "object",
    "properties": {
        "base": {"type": "number"},
        "growth": {"type": "number"},
        "max": {"type": "number"},
        "mod_max": {"type": "number"},
    }
}

###########################
# Core subschemas
###########################

bond_support_schema = {
    "type": "object",
    "properties": {
        "unit": {"type": "number"},
        "supported_by": {"type": "number"},
        "bonuses": {
            "type": "object",
            "properties": {
                "hit": {"type": "number"},
                "crit": {"type": "number"},
                "avo": {"type": "number"},
                "ddg": {"type": "number"}
            }
        }
    }
}

skill_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "game": {"type": "string"},
        "priority": {"type": "number"},
        "effects": {
            "type": "object",
            "properties": {
                "passive": {"type": ["string", "null"]},
                "before_combat": {"type": ["string", "null"]},
                "after_combat": {"type": ["string", "null"]},
                "before_attack": {"type": ["string", "null"]},
                "after_attack": {"type": ["string", "null"]},
                "before_attacked": {"type": ["string", "null"]},
                "after_attacked": {"type": ["string", "null"]},
                "turn_start": {"type": ["string", "null"]},
                "turn_end": {"type": ["string", "null"]},
                "use": {"type": ["string", "null"]},
                "equip": {"type": ["string", "null"]},
                "dequip": {"type": ["string", "null"]},
            }
        }
    }
}

item_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "prf_users": {"type": "array", "items": {"type": "number"}},
        "wt": {"type": "number"},
        "uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "equippable": {"type": "boolean"},
        "command": {"type": "string"},
        "effects": {"type": "array", "items": skill_schema}
    }
}

weapon_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "damage_type": {"type": "string", "enum": ["Physical", "Magical", "Fixed"]},
        "weapon_type": {"type": "string", "enum": weapon_types},
        "breaks_into": {"type": "number"},
        "rank": {"type": "string"},
        "prf_users": {"type": "array", "items": {"type": "number"}},
        "mt": {"type": "number"},
        "hit": {"type": "number"},
        "crit": {"type": "number"},
        "min_range": {"type": "number"},
        "max_range": {"type": "number"},
        "wt": {"type": "number"},
        "uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "effects": {"type": "array", "items": skill_schema}
    }
}

class_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "detail": {"type": "string"},
        "description": {"type": "string"},
        "game": {"type": "string"},
        "promotes_to": {"type": "array", "items": {"type": "number"}},
        "max_level": {"type": "number"},
        "class_strength": {"type": "number"},
        "class_exp": {"type": "number"},
        "promoted": {"type": "boolean"},
        "damage_types": {
            "type": "object",
            "properties": {
                "cavalry": {"type": "boolean"},
                "flying": {"type": "boolean"},
                "armored": {"type": "boolean"},
                "wyvern": {"type": "boolean"},
                "dragon": {"type": "boolean"},
                "infantry": {"type": "boolean"},
            }
        },
        "movement_costs": {
            "type": "object",
            "properties": {
                "floor": {"type": "number"},
                "forest": {"type": "number"},
                "thicket": {"type": "number"},
                "mountain": {"type": "number"},
                "peak": {"type": "number"},
                "cliff": {"type": "number"},
                "sand": {"type": "number"},
                "desert": {"type": "number"},
                "pillar": {"type": "number"},
                "wall": {"type": "number"},
                "fort": {"type": "number"},
                "gate": {"type": "number"},
                "throne": {"type": "number"},
                "grave": {"type": "number"},
                "river": {"type": "number"},
                "sea": {"type": "number"},
                "road": {"type": "number"},
                "building": {"type": "number"},
                "aerial": {"type": "number"},
                "wasteland": {"type": "number"},
            }
        },
        "stats": {
            "type": "object",
            "properties": {
                stat_name: class_stat_subschema for stat_name in stat_names
            },
        },
        "ranks": {
            "type": "object",
            "properties": {
                weapon_type: weapon_rank_subschema for weapon_type in weapon_types
            }
        },
        "skills": {
            "type": "array",
            "items": skill_schema
        }
    }
}

unit_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "sex": {"type": "string"},
        "game": {"type": "string"},
        "route": {"type": ["string", "null"]},
        "initial_class": class_schema,
        "base_classes": {"type": "array", "items": class_schema},
        "base_lv": {"type": "number"},
        "stats": {
            stat_name: unit_stat_subschema for stat_name in stat_names
        },
        "ranks": {
            weapon_type: {"type": "number"} for weapon_type in weapon_types
        },
        "affinity": {"type": "string", "enum": affinities},
        "bond_supports": {"type": "array", "items": bond_support_schema},
        "can_ranked_support": {"type": "array", "items": {"type": "number"}},
        "personal_skills": {"type": "array", "items": skill_schema},
        "skill_tolerance": {"type": "number"}
    }
}

#########################
# I/O Schemas
#########################

build_unit_schema = {
    "type": "object",
    "properties": {
        "base_unit": {"type": "number"},
        "nickname": {"type": "string"},
        "modifications": {
            "type": "array",
            "items": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "level_up"}
                        },
                        "required": ["action"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "promote"},
                            "into": {"type": "number"}
                        },
                        "required": ["action", "into"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_class"},
                            "into": {"type": "number"}
                        },
                        "required": ["action", "into"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "boost_stat"},
                            "stat": {"type": "string", "enum": stat_names},
                            "points": {"type": "number"}
                        },
                        "required": ["action", "stat", "points"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "build_support"},
                            "with": {"type": "number"}
                        },
                        "required": ["action", "with"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "boost_weapon_rank"},
                            "weapon_type": {"type": "string", "enum": weapon_types},
                            "points": {"type": "number"}
                        },
                        "required": ["action", "weapon_type", "points"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "apply_item"},
                            "item": {"type": "number"}
                        },
                        "required": ["action", "item"]
                    }
                ]
            }
        },
        "inventory": {
            "type": "array",
            "items": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string", "const": "weapon"},
                            "weapon": {"type": "number"},
                            "equipped": {"type": "boolean"}
                        },
                        "required": ["kind", "weapon", "equipped"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string", "const": "item"},
                            "item": {"type": "number"},
                            "equipped": {"type": "boolean"}
                        },
                        "required": ["kind", "item", "equipped"],
                    },
                ]
            }
        },
        "chosen_skills": {
            "type": "array",
            "items": {"type": "number"}
        }
    },
    "required": ["base_unit", "nickname", "modifications", "inventory", "chosen_skills"]
}

build_team_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "game": {"type": "string"},  # should be an abbreviation / primary key
        "validate": {"type": "boolean"},
        "limit": {"type": "boolean"},
        "units": {
            "type": "array",
            "items": build_unit_schema
        },
        "tactician_rank": {"type": "number"},
        "tactivian_affinity": {"type": "string", "enum": affinities}
    },
    "required": ["name", "game", "units"]
}

########################
# Built Schemas
########################

built_weapon_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "damage_type": {"type": "string", "enum": ["Physical", "Magical", "Fixed"]},
        "weapon_type": {"type": "string", "enum": weapon_types},
        "breaks_into": {"type": ["number", "null"]},
        "rank": {"type": "string"},
        "prf_users": {"type": "array", "items": {"type": "number"}},
        "mt": {"type": "number"},
        "hit": {"type": "number"},
        "crit": {"type": "number"},
        "min_range": {"type": "number"},
        "max_range": {"type": "number"},
        "wt": {"type": "number"},
        "uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "effects": {"type": "array", "items": skill_schema},
        "equipped": {"type": "boolean"},
        "inventory_id": {"type": "number"},
    }
}

built_item_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "prf_users": {"type": "array", "items": {"type": "number"}},
        "wt": {"type": "number"},
        "uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "equippable": {"type": "boolean"},
        "command": {"type": ["string", "null"]},
        "effects": {"type": "array", "items": skill_schema},
        "equipped": {"type": "boolean"},
        "inventory_id": {"type": "number"},
    }
}

built_unit_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "nickname": {"type": "string"},
        "base_unit": unit_schema,
        "class": class_schema,
        "level": {"type": "number"},
        "class_history": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "class": class_schema,
                    "levels": {"type": "number"}
                }
            }
        },
        "main_weapon_type": {"type": "string", "enum": weapon_types},
        "validated": {"type": "boolean"},
        "limited": {"type": "boolean"},
        "stat_boosts": {
            stat_name: {"type": "number"} for stat_name in stat_names
        },
        "rank_boosts": {
            weapon_type: {"type": "number"} for weapon_type in weapon_types
        },
        "weapons": {
            "type": "array",
            "items": built_weapon_schema,
        },
        "items": {
            "type": "array",
            "items": built_item_schema,
        },
        "extra_skills": {
            "type": "array",
            "items": skill_schema,
        },
        "instructions": build_unit_schema
    }
}

built_team_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "owner": {"type": "string"},
        "name": {"type": "string"},
        "units": {"type": "array", "items": built_unit_schema},
        "tactician_rank": {
            "affinity": {"type": "string"},
            "rank": {"type": "number"}
        }
    }
}
