"""
file: ranks.py

Contains methods for calculating the final weapon rank values of BuiltUnits.
"""
from typing import Dict
from ...models.build.BuiltUnit import BuiltUnit
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.core.Game import FireEmblemGame
from ...models.core.WeaponRank import WeaponRank, WeaponRankPointRequirement
from ...models.core.Weapon import Weapon, WeaponType


_rank_comp: Dict[str, int] = {
    WeaponRank.SS: 140,
    WeaponRank.S: 120,
    WeaponRank.A: 100,
    WeaponRank.B: 80,
    WeaponRank.C: 60,
    WeaponRank.D: 40,
    WeaponRank.E: 20,
    WeaponRank.NONE: 0,
    WeaponRank.PRF: -1,
}


def weapon_rank_from_points(game: FireEmblemGame, points: int, cap: str = WeaponRank.SS) -> str:
    """
    Returns the weapon rank that the given number of points equates to, given a total
    amount of weapon EXP. Returns a ValueError if the given game does not have weapon rank data.
    :param game: the game to check
    :param points: the number of points to check the weapon rank for
    :param cap: The maximum weapon rank attainable for this weapon type
    :return: the string corresponding to the weapon rank this much Weapon EXP adds up to
    """
    try:
        achieved_rank = max(
            WeaponRankPointRequirement.objects.filter(game=game),
            key=lambda r: (points >= r.points_required, r.points_required)
        ).weapon_rank
        return achieved_rank if _rank_comp[achieved_rank] <= _rank_comp[cap] else cap
    except ValueError:
        return WeaponRank.NONE


def unit_can_equip_weapon(game: FireEmblemGame, unit: ActiveUnit, weapon: ActiveWeapon) -> bool:
    """
    Returns True if the unit can equip the given weapon (either they are a Prf user, or
    their appropriate weapon level is high enough)
    :param game: the FireEmblemGame whose weapon rank mechanics to use for this check
    :param unit: An ActiveUnit
    :param weapon: An ActiveWeapon
    :return: True if this ActiveUnit has the appropriate weapon rank to use the given
        ActiveWeapon, or False otherwise
    """
    # if the unit is a Prf user of the weapon, the answer is automatically yes
    if unit.template.unit in weapon.template.prf_users.all():
        return True
    if weapon.template.rank != WeaponRank.PRF and (
            _rank_comp[weapon_rank_for_unit(game, weapon.template.weapon_type, unit)]
            >= _rank_comp[weapon.template.rank]):
        return True
    return False


def built_unit_can_equip_weapon(game: FireEmblemGame, unit: BuiltUnit, weapon: Weapon) -> bool:
    """
    Returns True if the unit can equip the given weapon (either they are a Prf user, or
    their appropriate weapon level is high enough)
    :param game: the FireEmblemGame whose weapon rank mechanics to use for this check
    :param unit: A BuiltUnit
    :param weapon: A Weapon
    :return: True if this BuiltUnit has the appropriate weapon rank to use the given
        Weapon, or False otherwise
    """
    # if the unit is a Prf user of the weapon, the answer is automatically yes
    if unit.unit in weapon.prf_users.all():
        return True
    if weapon.rank != WeaponRank.PRF and (
            _rank_comp[weapon_rank_for_built_unit(game, weapon.weapon_type, unit)] >= _rank_comp[weapon.rank]):
        return True
    return False


def weapon_rank_for_unit(game: FireEmblemGame, weapon_type: str, unit: ActiveUnit) -> str:
    """
    Calculates the total weapon rank, as a single number, of the given active unit for 
    the given weapon, and returns it. Throws a KeyError if weapon type does not exist.
    :param game: The Fire Emblem Game whose mechanics to use for calculating weapon rank
    :param weapon_type: an existent weapon type
    :param unit: an ActiveUnit to check weapon rank for
    :return: the unit's weapon rank, as a letter (e.g. 'SS', 'S', 'A', ..., 'E', '--')
    """
    return {
        WeaponType.SWORD: sword_rank,
        WeaponType.LANCE: lance_rank,
        WeaponType.AXE: axe_rank,
        WeaponType.BOW: bow_rank,
        WeaponType.GAUNTLET: gauntlet_rank,
        WeaponType.HIDDEN: hidden_rank,
        WeaponType.FIRE: fire_rank,
        WeaponType.WIND: wind_rank,
        WeaponType.THUNDER: thunder_rank,
        WeaponType.DARK: dark_rank,
        WeaponType.LIGHT: light_rank,
        WeaponType.ANIMA: anima_rank,
        WeaponType.BLACK: black_rank,
        WeaponType.WHITE: white_rank,
        WeaponType.STAFF: staff_rank,
        WeaponType.DRAGONSTONE: dragonstone_rank,
        WeaponType.BEAST: beast_rank,
        WeaponType.SPECIAL: special_rank
    }[weapon_type](game, unit)


def weapon_rank_for_built_unit(game: FireEmblemGame, weapon_type: str, unit: BuiltUnit) -> str:
    """
    Calculates the currently-attained weapon rank for the given Built Unit
    :param game: the game whose mechanics to use for calculating weapon rank
    :param weapon_type: an existent weapon type
    :param unit: a BuiltWeapon to check for
    :return: the unit's current weapon rank without modifiers, as a letter
    """
    return weapon_rank_from_points(game, {
        WeaponType.SWORD: sword_points,
        WeaponType.LANCE: lance_points,
        WeaponType.AXE: axe_points,
        WeaponType.BOW: bow_points,
        WeaponType.GAUNTLET: gauntlet_points,
        WeaponType.HIDDEN: hidden_points,
        WeaponType.TOME: tome_points,
        WeaponType.FIRE: fire_points,
        WeaponType.WIND: wind_points,
        WeaponType.THUNDER: thunder_points,
        WeaponType.DARK: dark_points,
        WeaponType.LIGHT: light_points,
        WeaponType.ANIMA: anima_points,
        WeaponType.BLACK: black_points,
        WeaponType.WHITE: white_points,
        WeaponType.STAFF: staff_points,
        WeaponType.DRAGONSTONE: dragonstone_points,
        WeaponType.BEAST: beast_points,
        WeaponType.SPECIAL: special_points
    }[weapon_type](unit), game.max_weapon_rank)
    
    
def sword_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's sword rank
    """
    unit_base = unit.unit.base_rank_sword
    class_base = unit.unit_class.base_rank_sword
    unit_growth = unit.boost_rank_sword
    return unit_base + class_base + unit_growth
    
    
def sword_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's sword rank
    """
    mod = unit.mod_rank_sword
    cap = unit.template.unit_class.max_rank_sword
    return weapon_rank_from_points(game, sword_points(unit.template) + mod, cap)


def lance_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's lance rank
    """
    unit_base = unit.unit.base_rank_lance
    class_base = unit.unit_class.base_rank_lance
    unit_growth = unit.boost_rank_lance
    return unit_base + class_base + unit_growth


def lance_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's lance rank
    """
    mod = unit.mod_rank_lance
    cap = unit.template.unit_class.max_rank_lance
    return weapon_rank_from_points(game, lance_points(unit.template) + mod, cap)


def axe_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's axe rank
    """
    unit_base = unit.unit.base_rank_axe
    class_base = unit.unit_class.base_rank_axe
    unit_growth = unit.boost_rank_axe
    return unit_base + class_base + unit_growth


def axe_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's axe rank
    """
    mod = unit.mod_rank_axe
    cap = unit.template.unit_class.max_rank_axe
    return weapon_rank_from_points(game, axe_points(unit.template) + mod, cap)


def bow_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's bow rank
    """
    unit_base = unit.unit.base_rank_bow
    class_base = unit.unit_class.base_rank_bow
    unit_growth = unit.boost_rank_bow
    return unit_base + class_base + unit_growth


def bow_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's bow rank
    """
    mod = unit.mod_rank_bow
    cap = unit.template.unit_class.max_rank_bow
    return weapon_rank_from_points(game, bow_points(unit.template) + mod, cap)


def gauntlet_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's gauntlet rank
    """
    unit_base = unit.unit.base_rank_gauntlet
    class_base = unit.unit_class.base_rank_gauntlet
    unit_growth = unit.boost_rank_gauntlet
    return unit_base + class_base + unit_growth


def gauntlet_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's gauntlet rank
    """
    mod = unit.mod_rank_gauntlet
    cap = unit.template.unit_class.max_rank_gauntlet
    return weapon_rank_from_points(game, gauntlet_points(unit.template) + mod, cap)


def hidden_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's hidden rank
    """
    unit_base = unit.unit.base_rank_hidden
    class_base = unit.unit_class.base_rank_hidden
    unit_growth = unit.boost_rank_hidden
    return unit_base + class_base + unit_growth


def hidden_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's hidden rank
    """
    mod = unit.mod_rank_hidden
    cap = unit.template.unit_class.max_rank_hidden
    return weapon_rank_from_points(game, hidden_points(unit.template) + mod, cap)


def tome_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's Tome rank
    """
    unit_base = unit.unit.base_rank_tome
    class_base = unit.unit_class.base_rank_tome
    unit_growth = unit.boost_rank_tome
    return unit_base + class_base + unit_growth


def tome_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's fire rank
    """
    mod = unit.mod_rank_tome
    cap = unit.template.unit_class.max_rank_tome
    return weapon_rank_from_points(game, tome_points(unit.template) + mod, cap)


def fire_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's fire rank
    """
    unit_base = unit.unit.base_rank_fire
    class_base = unit.unit_class.base_rank_fire
    unit_growth = unit.boost_rank_fire
    return unit_base + class_base + unit_growth


def fire_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's fire rank
    """
    mod = unit.mod_rank_fire
    cap = unit.template.unit_class.max_rank_fire
    return weapon_rank_from_points(game, fire_points(unit.template) + mod, cap)


def wind_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's wind rank
    """
    unit_base = unit.unit.base_rank_wind
    class_base = unit.unit_class.base_rank_wind
    unit_growth = unit.boost_rank_wind
    return unit_base + class_base + unit_growth


def wind_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's wind rank
    """
    mod = unit.mod_rank_wind
    cap = unit.template.unit_class.max_rank_wind
    return weapon_rank_from_points(game, wind_points(unit.template) + mod, cap)


def thunder_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's thunder rank
    """
    unit_base = unit.unit.base_rank_thunder
    class_base = unit.unit_class.base_rank_thunder
    unit_growth = unit.boost_rank_thunder
    return unit_base + class_base + unit_growth


def thunder_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's thunder rank
    """
    mod = unit.mod_rank_thunder
    cap = unit.template.unit_class.max_rank_thunder
    return weapon_rank_from_points(game, thunder_points(unit.template) + mod, cap)


def light_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's light rank
    """
    unit_base = unit.unit.base_rank_light
    class_base = unit.unit_class.base_rank_light
    unit_growth = unit.boost_rank_light
    return unit_base + class_base + unit_growth


def light_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's light rank
    """
    mod = unit.mod_rank_light
    cap = unit.template.unit_class.max_rank_light
    return weapon_rank_from_points(game, light_points(unit.template) + mod, cap)


def dark_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's dark rank
    """
    unit_base = unit.unit.base_rank_dark
    class_base = unit.unit_class.base_rank_dark
    unit_growth = unit.boost_rank_dark
    return unit_base + class_base + unit_growth


def dark_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's dark rank
    """
    mod = unit.mod_rank_dark
    cap = unit.template.unit_class.max_rank_dark
    return weapon_rank_from_points(game, dark_points(unit.template) + mod, cap)


def anima_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's anima rank
    """
    unit_base = unit.unit.base_rank_anima
    class_base = unit.unit_class.base_rank_anima
    unit_growth = unit.boost_rank_anima
    return unit_base + class_base + unit_growth


def anima_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's anima rank
    """
    mod = unit.mod_rank_anima
    cap = unit.template.unit_class.max_rank_anima
    return weapon_rank_from_points(game, anima_points(unit.template) + mod, cap)


def black_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's black rank
    """
    unit_base = unit.unit.base_rank_black
    class_base = unit.unit_class.base_rank_black
    unit_growth = unit.boost_rank_black
    return unit_base + class_base + unit_growth


def black_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's black rank
    """
    mod = unit.mod_rank_black
    cap = unit.template.unit_class.max_rank_black
    return weapon_rank_from_points(game, black_points(unit.template) + mod, cap)


def white_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's white rank
    """
    unit_base = unit.unit.base_rank_white
    class_base = unit.unit_class.base_rank_white
    unit_growth = unit.boost_rank_white
    return unit_base + class_base + unit_growth


def white_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's white rank
    """
    mod = unit.mod_rank_white
    cap = unit.template.unit_class.max_rank_white
    return weapon_rank_from_points(game, white_points(unit.template) + mod, cap)


def staff_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's staff rank
    """
    unit_base = unit.unit.base_rank_staff
    class_base = unit.unit_class.base_rank_staff
    unit_growth = unit.boost_rank_staff
    return unit_base + class_base + unit_growth


def staff_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's staff rank
    """
    mod = unit.mod_rank_staff
    cap = unit.template.unit_class.max_rank_staff
    return weapon_rank_from_points(game, staff_points(unit.template) + mod, cap)


def dragonstone_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's dragonstone rank
    """
    unit_base = unit.unit.base_rank_dragonstone
    class_base = unit.unit_class.base_rank_dragonstone
    unit_growth = unit.boost_rank_dragonstone
    return unit_base + class_base + unit_growth


def dragonstone_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's dragonstone rank
    """
    mod = unit.mod_rank_dragonstone
    cap = unit.template.unit_class.max_rank_dragonstone
    return weapon_rank_from_points(game, dragonstone_points(unit.template) + mod, cap)


def beast_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's beast rank
    """
    unit_base = unit.unit.base_rank_beast
    class_base = unit.unit_class.base_rank_beast
    unit_growth = unit.boost_rank_beast
    return unit_base + class_base + unit_growth


def beast_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's beast rank
    """
    mod = unit.mod_rank_beast
    cap = unit.template.unit_class.max_rank_beast
    return weapon_rank_from_points(game, beast_points(unit.template) + mod, cap)


def special_points(unit: BuiltUnit) -> int:
    """
    Calculates and returns the given BuiltUnit's special rank
    """
    unit_base = unit.unit.base_rank_special
    class_base = unit.unit_class.base_rank_special
    unit_growth = unit.boost_rank_special
    return unit_base + class_base + unit_growth


def special_rank(game: FireEmblemGame, unit: ActiveUnit) -> str:
    """
    Calculates and returns the given ActiveUnit's special rank
    """
    mod = unit.mod_rank_special
    cap = unit.template.unit_class.max_rank_special
    return weapon_rank_from_points(game, special_points(unit.template) + mod, cap)
