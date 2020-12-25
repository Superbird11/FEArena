"""
file: teambuilder/helper.py

Helper methods for teambuilding
"""
from django.core.exceptions import ObjectDoesNotExist
from ...models.build.BuiltUnit import BuiltUnit
from ...models.build.BuiltTeam import BuiltTeam
from ...models.core.Weapon import WeaponType
from ...models.core.Class import Class
from ...models.core.PromotionBonus import PromotionBonus
from ...models.core.Game import FireEmblemGame
from ...models.core.WeaponRank import WeaponRankPointRequirement
from ..calc import ranks
import logging


def apply_stat_boost(unit: BuiltUnit, stat_name: str, amount: int):
    """
    Takes the given name of a stat, and applies the given boost to that stat for this BuiltUnit.
    :param unit: BuiltUnit to modify
    :param stat_name: name of stat (str, spd, etc.), from stat_names in api/teambuilder.schemas
    :param amount: amount to boost stat by
    """
    # ["hp", "str", "mag", "skl", "spd", "luk", "def", "res", "cha", "con", "mov"]
    if stat_name == "hp":
        unit.boosts_hp += amount
    elif stat_name == "str":
        unit.boosts_str += amount
    elif stat_name == "mag":
        unit.boosts_mag += amount
    elif stat_name == "skl":
        unit.boosts_skl += amount
    elif stat_name == "luk":
        unit.boosts_luk += amount
    elif stat_name == "spd":
        unit.boosts_spd += amount
    elif stat_name == "def":
        unit.boosts_def += amount
    elif stat_name == "res":
        unit.boosts_res += amount
    elif stat_name == "cha":
        unit.boosts_cha += amount
    elif stat_name == "con":
        unit.boosts_con += amount
    elif stat_name == "mov":
        unit.boosts_mov += amount
    else:
        raise ValueError(f"Unrecognized stat {stat_name}")


def apply_rank_boost(game: FireEmblemGame, unit: BuiltUnit, weapon_type: str, amount: int, apply_limits: bool):
    """
    Takes the given name of a weapon type, and applies the given boost to the BuiltUnit's
    corresponding weapon rank. Returns the final weapon rank this results in
    :param game: the game whose mechanics to use for mutually exclusive S-rank calculations
    :param unit: BuiltUnit to modify
    :param weapon_type: name of weapon type (Sword, Lance, etc.)
    :param amount: number of points to boost weapon rank by
    :param apply_limits: should apply weapon rank limits if they exist
    :return: the total number of boost points the unit now has in this rank
    """
    if weapon_type == WeaponType.SWORD:
        unit.boost_rank_sword += amount
    elif weapon_type == WeaponType.LANCE:
        unit.boost_rank_lance += amount
    elif weapon_type == WeaponType.AXE:
        unit.boost_rank_axe += amount
    elif weapon_type == WeaponType.BOW:
        unit.boost_rank_bow += amount
    elif weapon_type == WeaponType.GAUNTLET:
        unit.boost_rank_gauntlet += amount
    elif weapon_type == WeaponType.HIDDEN:
        unit.boost_rank_hidden += amount
    elif weapon_type == WeaponType.TOME:
        unit.boost_rank_tome += amount
    elif weapon_type == WeaponType.FIRE:
        unit.boost_rank_fire += amount
    elif weapon_type == WeaponType.THUNDER:
        unit.boost_rank_thunder += amount
    elif weapon_type == WeaponType.WIND:
        unit.boost_rank_wind += amount
    elif weapon_type == WeaponType.LIGHT:
        unit.boost_rank_light += amount
    elif weapon_type == WeaponType.DARK:
        unit.boost_rank_dark += amount
    elif weapon_type == WeaponType.ANIMA:
        unit.boost_rank_anima += amount
    elif weapon_type == WeaponType.BLACK:
        unit.boost_rank_black += amount
    elif weapon_type == WeaponType.WHITE:
        unit.boost_rank_white += amount
    elif weapon_type == WeaponType.STAFF:
        unit.boost_rank_staff += amount
    elif weapon_type == WeaponType.DRAGONSTONE:
        unit.boost_rank_dragonstone += amount
    elif weapon_type == WeaponType.BEAST:
        unit.boost_rank_beast += amount
    elif weapon_type == WeaponType.SPECIAL:
        unit.boost_rank_special += amount
    else:
        raise ValueError(f"Unrecognized weapon type f{weapon_type}")
    # handle the case of mutually-exclusive S or SS ranks, if applicable
    if ranks.weapon_rank_for_built_unit(game, weapon_type, unit) == game.max_weapon_rank:
        if not unit.main_weapon_type:
            unit.main_weapon_type = weapon_type
        elif WeaponType != unit.main_weapon_type and not apply_limits or not game.mutually_exclusive_max_weapon_rank:
            set_rank_to_below_game_max(game, unit, weapon_type)


def set_rank_to_below_game_max(game: FireEmblemGame, unit: BuiltUnit, weapon_type: str):
    """
    Sets the weapon rank for the given weapon to one point below the given game's requirement
    for its max weapon rank. If the given game doesn't have point-gated weapon ranks, then
    does nothing.
    :param game: the FireEmblemGame whose max ranks to check
    :param unit: BuiltUnit to modify
    :param weapon_type: name of weapon type (Sword, Lance, etc.)
    :return: the total number of boost points the unit now has in this rank
    """
    # get number to set it to
    try:
        max_points = WeaponRankPointRequirement.objects.get(game=game, weapon_rank=game.max_weapon_rank)\
                         .points_required - 1
    except ObjectDoesNotExist:
        logging.warning(f"Failed to find a point requirement for game {game.name}'s max weapon rank")
        return
    if weapon_type == WeaponType.SWORD:
        unit.boost_rank_sword = max_points
    elif weapon_type == WeaponType.LANCE:
        unit.boost_rank_lance = max_points
    elif weapon_type == WeaponType.AXE:
        unit.boost_rank_axe = max_points
    elif weapon_type == WeaponType.BOW:
        unit.boost_rank_bow = max_points
    elif weapon_type == WeaponType.GAUNTLET:
        unit.boost_rank_gauntlet = max_points
    elif weapon_type == WeaponType.HIDDEN:
        unit.boost_rank_hidden = max_points
    elif weapon_type == WeaponType.TOME:
        unit.boost_rank_tome = max_points
    elif weapon_type == WeaponType.FIRE:
        unit.boost_rank_fire = max_points
    elif weapon_type == WeaponType.THUNDER:
        unit.boost_rank_thunder = max_points
    elif weapon_type == WeaponType.WIND:
        unit.boost_rank_wind = max_points
    elif weapon_type == WeaponType.LIGHT:
        unit.boost_rank_light = max_points
    elif weapon_type == WeaponType.DARK:
        unit.boost_rank_dark = max_points
    elif weapon_type == WeaponType.ANIMA:
        unit.boost_rank_anima = max_points
    elif weapon_type == WeaponType.BLACK:
        unit.boost_rank_black = max_points
    elif weapon_type == WeaponType.WHITE:
        unit.boost_rank_white = max_points
    elif weapon_type == WeaponType.STAFF:
        unit.boost_rank_staff = max_points
    elif weapon_type == WeaponType.DRAGONSTONE:
        unit.boost_rank_dragonstone = max_points
    elif weapon_type == WeaponType.BEAST:
        unit.boost_rank_beast = max_points
    elif weapon_type == WeaponType.SPECIAL:
        unit.boost_rank_special = max_points
    else:
        raise ValueError(f"Unrecognized weapon type f{weapon_type}")


def apply_promotion_bonuses(game: FireEmblemGame, unit: BuiltUnit, from_class: Class, to_class: Class,
                            apply_limits: bool):
    """
    Retrieves the promotion bonuses in play for the promotion between the given classes,
    and applies them as boosts to the unit, if they exist.
    Does accommodate for setting ranks to below rank max,
    :param game: the game to apply promotion in
    :param unit: unit to modify
    :param from_class: class being promoted out of
    :param to_class: class being promoted into
    :param apply_limits: apply limits when applying rank boost?
    """
    try:
        promo_bonus: PromotionBonus = PromotionBonus.objects.get(from_class=from_class, to_class=to_class)
    except ObjectDoesNotExist:
        return
    apply_stat_boost(unit, 'hp', promo_bonus.bonus_hp)
    apply_stat_boost(unit, 'str', promo_bonus.bonus_str)
    apply_stat_boost(unit, 'mag', promo_bonus.bonus_mag)
    apply_stat_boost(unit, 'skl', promo_bonus.bonus_skl)
    apply_stat_boost(unit, 'spd', promo_bonus.bonus_spd)
    apply_stat_boost(unit, 'luk', promo_bonus.bonus_luk)
    apply_stat_boost(unit, 'def', promo_bonus.bonus_def)
    apply_stat_boost(unit, 'res', promo_bonus.bonus_res)
    apply_stat_boost(unit, 'cha', promo_bonus.bonus_cha)
    apply_stat_boost(unit, 'con', promo_bonus.bonus_con)
    apply_stat_boost(unit, 'mov', promo_bonus.bonus_mov)

    apply_rank_boost(game, unit, WeaponType.SWORD, promo_bonus.bonus_sword, apply_limits)
    apply_rank_boost(game, unit, WeaponType.LANCE, promo_bonus.bonus_lance, apply_limits)
    apply_rank_boost(game, unit, WeaponType.AXE, promo_bonus.bonus_axe, apply_limits)
    apply_rank_boost(game, unit, WeaponType.BOW, promo_bonus.bonus_bow, apply_limits)
    apply_rank_boost(game, unit, WeaponType.GAUNTLET, promo_bonus.bonus_gauntlet, apply_limits)
    apply_rank_boost(game, unit, WeaponType.HIDDEN, promo_bonus.bonus_hidden, apply_limits)
    apply_rank_boost(game, unit, WeaponType.TOME, promo_bonus.bonus_tome, apply_limits)
    apply_rank_boost(game, unit, WeaponType.FIRE, promo_bonus.bonus_fire, apply_limits)
    apply_rank_boost(game, unit, WeaponType.THUNDER, promo_bonus.bonus_thunder, apply_limits)
    apply_rank_boost(game, unit, WeaponType.WIND, promo_bonus.bonus_wind, apply_limits)
    apply_rank_boost(game, unit, WeaponType.ANIMA, promo_bonus.bonus_anima, apply_limits)
    apply_rank_boost(game, unit, WeaponType.LIGHT, promo_bonus.bonus_light, apply_limits)
    apply_rank_boost(game, unit, WeaponType.DARK, promo_bonus.bonus_dark, apply_limits)
    apply_rank_boost(game, unit, WeaponType.STAFF, promo_bonus.bonus_staff, apply_limits)
    apply_rank_boost(game, unit, WeaponType.BLACK, promo_bonus.bonus_black, apply_limits)
    apply_rank_boost(game, unit, WeaponType.WHITE, promo_bonus.bonus_white, apply_limits)
    apply_rank_boost(game, unit, WeaponType.DRAGONSTONE, promo_bonus.bonus_dragonstone, apply_limits)
    apply_rank_boost(game, unit, WeaponType.BEAST, promo_bonus.bonus_beast, apply_limits)
    apply_rank_boost(game, unit, WeaponType.SPECIAL, promo_bonus.bonus_other, apply_limits)


def save_built_unit(unit: BuiltUnit):
    """
    Saves the given BuiltUnit to the database, including dependent objects
    """
    for built_weapon in unit.weapons.all():
        built_weapon.save()
    for built_item in unit.items.all():
        built_item.save()
    # for built_class in unit.unit_class_history.all():
    #     built_class.save()
    unit.save()


def delete_built_team(team: BuiltTeam):
    """
    Removes the given team and all dependent objects from the database
    """
    logging.debug(f"Deleting BuiltTeam {team.id} and all sub-objects from database")
    for unit in team.units.all():
        for weapon in unit.weapons.all():
            weapon.delete()
        for item in unit.items.all():
            item.delete()
        unit.delete()
    team.delete()


__all__ = ['apply_stat_boost', 'apply_rank_boost', 'set_rank_to_below_game_max', 'apply_promotion_bonuses',
           'delete_built_team', 'save_built_unit']
