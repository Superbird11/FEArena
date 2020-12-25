"""
file: api/arena/schemas.py

Contains JSON schemas to control the format of input and output.

"""
########################################
# Model Representation Schemas
########################################
from ..teambuilder.schemas import skill_schema, weapon_types, class_schema

active_item_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "inventory_id": {"type": "number"},
        "prf": {"type": "array", "items": {"type": "string"}},  # unit names
        "wt": {"type": "number"},
        "total_uses": {"type": "number"},
        "current_uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "equippable": {"type": "boolean"},
        "equipped": {"type": "boolean"},
        "skills": {"type": "array", "items": skill_schema}
    }
}

active_weapon_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "game": {"type": "string"},
        "description": {"type": "string"},
        "inventory_id": {"type": "number"},
        "damage_type": {  # models.core.Weapon.WeaponDamageType
            "type": "string",
            "enum": ["Physical", "Magical", "Fixed"]
        },
        "weapon_type": {  # models.core.Weapon.WeaponType
            "type": "string",
            "enum": weapon_types
        },
        "rank": {  # models.core.WeaponRank.WeaponRank
            "type": "string",
            "enum": ["SS", "S", "A", "B", "C", "D", "E", "Prf", "--"]
        },
        "prf": {"type": "array", "items": {"type": "string"}},  # unit names
        "mt": {"type": "number"},
        "hit": {"type": "number"},
        "crit": {"type": "number"},
        "min_range": {"type": "number"},
        "max_range": {"type": "number"},
        "wt": {"type": "number"},
        "total_uses": {"type": "number"},
        "current_uses": {"type": "number"},
        "usable": {"type": "boolean"},
        "equipped": {"type": "boolean"},
        "skills": {"type": "array", "items": skill_schema}
    }
}

unit_stat_subschema = {
    "type": "object",
    "properties": {
        "unit_base": {"type": "number"},
        "class_base": {"type": "number"},
        "unit_growth": {"type": "number"},
        "all_class_growths": {"type": "array", "items": {"type": "number"}},
        "boosts": {"type": "number"},
        "modifiers": {"type": "number"},
        "unit_max": {"type": "number"},
        "unit_max_mod": {"type": "number"},
        "class_max": {"type": "number"},
    }
}

unit_weapon_rank_subschema = {
    "type": "object",
    "properties": {
        "unit_base": {"type": "number"},
        "class_base": {"type": "number"},
        "boosts": {"type": "number"},
        "modifiers": {"type": "number"}
    }
}

active_unit_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "nickname": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "sex": {"type": "string"},
        "game": {"type": "string"},
        "route": {"type": "string"},
        "class": class_schema,
        "level": {"type": "number"},
        "all_class_levels": {"type": "array", "items": {"type": "number"}},
        "current_hp": {"type": "number"},
        "stats": {
            "type": "object",
            "properties": {
                "level": {"type": "number"},
                "hp": unit_stat_subschema,
                "str": unit_stat_subschema,
                "mag": unit_stat_subschema,
                "skl": unit_stat_subschema,
                "spd": unit_stat_subschema,
                "luk": unit_stat_subschema,
                "def": unit_stat_subschema,
                "res": unit_stat_subschema,
                "cha": unit_stat_subschema,
                "con": unit_stat_subschema,
                "mov": unit_stat_subschema,
            }
        },
        "weapon_ranks": {
            "type": "object",
            "properties": {
                "sword": unit_weapon_rank_subschema,
                "lance": unit_weapon_rank_subschema,
                "axe": unit_weapon_rank_subschema,
                "bow": unit_weapon_rank_subschema,
                "gauntlet": unit_weapon_rank_subschema,
                "hidden": unit_weapon_rank_subschema,
                "tome": unit_weapon_rank_subschema,
                "fire": unit_weapon_rank_subschema,
                "wind": unit_weapon_rank_subschema,
                "thunder": unit_weapon_rank_subschema,
                "dark": unit_weapon_rank_subschema,
                "light": unit_weapon_rank_subschema,
                "anima": unit_weapon_rank_subschema,
                "black": unit_weapon_rank_subschema,
                "white": unit_weapon_rank_subschema,
                "staff": unit_weapon_rank_subschema,
                "dragonstone": unit_weapon_rank_subschema,
                "beast": unit_weapon_rank_subschema,
                "special": unit_weapon_rank_subschema,
            }
        },
        "inventory": {
            "type": "object",
            "properties": {
                "weapons": {"type": "array", "items": active_weapon_schema},
                "items": {"type": "array", "items": active_item_schema},
            }
        },
        "personal_skills": {"type": "array", "items": skill_schema},
        "extra_skills": {"type": "array", "items": skill_schema},
        "temporary_skills": {"type": "array", "items": skill_schema},
    }
}

active_team_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "user": {"type": "string"},
        "name": {"type": "string"},
        "units": {"type": "array", "items": active_unit_schema},
        "score": {"type": "number"},
    }
}

active_arena_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "game": {"type": "string"},
        "format": {"type": "string"},
        "teams": {"type": "array", "items": active_team_schema},
        "turn": {"type": "number"},
        "phase": {"type": "phase"},
    }
}

########################################
# API input/output schemas
########################################

request_match_schema = {
    "type": "object",
    "properties": {
        "players": {"type": "number"},
        "format": {"type": "string"},
        "team_id": {"type": "number"},
    }
}

action_input_schema = {
    "type": "object",
    "properties": {
        "unit": {"type": "number"},
        "actions": {
            "type": "array",
            "items": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "equip_weapon"},
                            "weapon": {"type": "number"}
                        },
                        "required": ["action", "weapon"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "equip_item"},
                            "item": {"type": "number"}
                        },
                        "required": ["action", "item"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "discard_weapon"},
                            "weapon": {"type": "number"}
                        },
                        "required": ["action", "weapon"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "discard_item"},
                            "item": {"type": "number"}
                        },
                        "required": ["action", "item"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "attack"},
                            "target": {"type": "number"},
                            "with_weapon": {"type": "number"},
                            "range": {"type": "number"}
                        },
                        "required": ["action", "target", "with_weapon", "range"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "use_weapon"},
                            "weapon": {"type": "number"},
                            "target": {"type": "number"},
                            "extra_data": {"type": "string"},
                        },
                        "required": ["action", "weapon"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "use_item"},
                            "item": {"type": "number"},
                            "target": {"type": "number"},
                            "extra_data": {"type": "string"},
                        },
                        "required": ["action", "item"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "use_skill"},
                            "skill": {"type": "number"},   # skill id (primary key)
                            "target": {"type": "number"},
                            "extra_data": {"type": "string"}
                        },
                        "required": ["action", "skill"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "wait"}
                        },
                        "required": ["action", "wait"]
                    }
                ]
            }
        }
    },
    "required": ["unit", "actions"]
}


action_output_schema = {
    "type": "object",
    "properties": {
        "changes": {
            "type": "array",
            "items": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "begin_turn"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "end_turn"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "continue_turn"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_turn"},
                            "turn": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_phase"},
                            "phase": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "victory"},
                            "team": {"type": "number"},
                            "turns": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "unequip_weapon"},
                            "unit": {"type": "number"},
                            "weapon": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "equip_weapon"},
                            "unit": {"type": "number"},
                            "weapon": {"type": "number"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_weapon_inventory_id"},
                            "unit": {"type": "number"},
                            "weapon": {"type": "number"},
                            "new_id": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_item_inventory_id"},
                            "unit": {"type": "number"},
                            "item": {"type": "number"},
                            "new_id": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_weapon_uses"},
                            "weapon": {"type": "number"},
                            "new_uses": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "change_item_uses"},
                            "item": {"type": "number"},
                            "new_uses": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "remove_weapon"},
                            "weapon": {"type": "number"},
                            "unit": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "remove_item"},
                            "item": {"type": "number"},
                            "unit": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "replace_weapon"},
                            "weapon": {"type": "number"},
                            "new_data": {"type": "string"}, # active_weapon_schema
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "effective_attacks"},
                            "unit": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "activate_skill"},
                            "skill": {"type": "string"},
                            "data": {"type": ["string", "number", "null"]},  # skill-specific data
                            "show": {"type": "boolean"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "steal_item"},
                            "unit": {"type": "number"},
                            "unit": {"type": "number"},
                            "from": {"type": "number"},
                            "item": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "start_combat"},
                            "attacker": {"type": "number"},
                            "attacker_weapon": {"type": "number"},
                            "attacker_displayed_dmg": {"type": "number"},
                            "attacker_displayed_hit": {"type": "number"},
                            "attacker_displayed_crit": {"type": "number"},
                            "attacker_displayed_atk": {"type": "number"},
                            "attacker_displayed_prt": {"type": "number"},
                            "attacker_displayed_rsl": {"type": "number"},
                            "defender_weapon": {"type": ["number", "null"]},
                            "defender_displayed_dmg": {"type": "number"},
                            "defender_displayed_hit": {"type": "number"},
                            "defender_displayed_crit": {"type": "number"},
                            "defender_displayed_atk": {"type": "number"},
                            "defender_displayed_prt": {"type": "number"},
                            "defender_displayed_rsl": {"type": "number"},
                            "defender": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "end_combat"},
                            "attacker_team": {"type": "number"},
                            "points_to_attacker": {"type": "number"},
                            "defender_team": {"type": "number"},
                            "points_to_defender": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "attack"},
                            "by_unit": {"type": "number"},
                            "weapon": {"type": "number"},
                            "against_unit": {"type": "number"},
                            "miss": {"type": "boolean"},
                            "crit": {"type": "boolean"},
                            "dmg": {"type": "number"},
                            "skills": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "restore_health"},
                            "unit": {"type": "number"},
                            "health": {"type": "number"}
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "kill_unit"},
                            "team": {"type": "number"},
                            "unit": {"type": "number"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "wait"},
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "const": "points_for_survival"},
                            "unit": {"type": "number"},
                            "team": {"type": "number"},
                        }
                    }
                ]
            }
        }
    }
}
