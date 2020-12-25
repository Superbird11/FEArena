from django.core.exceptions import ObjectDoesNotExist
from typing import Union
from ...models.core.Game import FireEmblemGame
from ...models.core.Game import WeaponTriangleType
from ...models.core.WeaponTriangleBonus import WeaponTriangleBonus
from ...models.core.WeaponRankBonus import WeaponRankBonus
from ...models.core.Weapon import WeaponType
from ...models.play.ActiveUnit import ActiveUnit
from . import ranks


def weapon_triangle_status(game: FireEmblemGame, unit: str, enemy: str) -> Union[bool, None]:
    """
    Using the weapon triangle for the given game, determines whether a
    weapon triangle advantage exists.
    :param game: game whose weapon triangle mechanics to use
    :param unit: The unit's weapon type
    :param enemy: The opponent's weapon type
    :return: True if unit has WTA over the opponent; False if the reverse is true; None if neutral
    """
    wt_type = game.weapon_triangle
    if wt_type == WeaponTriangleType.NONE:
        return None
    else:
        # all other weapon triangle types have the physical weapon triangle, at least
        if any([
            unit == WeaponType.SWORD and enemy == WeaponType.LANCE,
            unit == WeaponType.LANCE and enemy == WeaponType.AXE,
            unit == WeaponType.AXE and enemy == WeaponType.SWORD,
        ]):
            return False
        elif any([
            unit == WeaponType.SWORD and enemy == WeaponType.AXE,
            unit == WeaponType.LANCE and enemy == WeaponType.SWORD,
            unit == WeaponType.AXE and enemy == WeaponType.LANCE,
        ]):
            return True
        # check type of magic weapon triangle
        if wt_type == WeaponTriangleType.MAGIC_ANIMA_SINGLE:
            if any([
                unit == WeaponType.FIRE and enemy in (WeaponType.THUNDER, WeaponType.LIGHT, WeaponType.DARK),
                unit == WeaponType.THUNDER and enemy in (WeaponType.WIND, WeaponType.LIGHT, WeaponType.DARK),
                unit == WeaponType.WIND and enemy in (WeaponType.FIRE, WeaponType.LIGHT, WeaponType.DARK),
            ]):
                return False
            elif any([
                enemy == WeaponType.FIRE and unit in (WeaponType.THUNDER, WeaponType.LIGHT, WeaponType.DARK),
                enemy == WeaponType.THUNDER and unit in (WeaponType.WIND, WeaponType.LIGHT, WeaponType.DARK),
                enemy == WeaponType.WIND and unit in (WeaponType.FIRE, WeaponType.LIGHT, WeaponType.DARK),
            ]):
                return True
        elif wt_type == WeaponTriangleType.MAGIC_TRINITY_SINGLE:
            if any([
                unit == WeaponType.ANIMA and enemy == WeaponType.DARK,
                unit == WeaponType.DARK and enemy == WeaponType.LIGHT,
                unit == WeaponType.LIGHT and enemy == WeaponType.ANIMA
            ]):
                return False
            elif any([
                enemy == WeaponType.ANIMA and unit == WeaponType.DARK,
                enemy == WeaponType.DARK and unit == WeaponType.LIGHT,
                enemy == WeaponType.LIGHT and unit == WeaponType.ANIMA
            ]):
                return True
        elif wt_type == WeaponTriangleType.MAGIC_DOUBLE:
            if any([
                unit == WeaponType.FIRE and enemy in (WeaponType.THUNDER, WeaponType.DARK),
                unit == WeaponType.THUNDER and enemy in (WeaponType.WIND, WeaponType.DARK),
                unit == WeaponType.WIND and enemy in (WeaponType.FIRE, WeaponType.DARK),
                unit == WeaponType.LIGHT and enemy in (WeaponType.THUNDER, WeaponType.FIRE, WeaponType.WIND),
                unit == WeaponType.DARK and enemy == WeaponType.LIGHT
            ]):
                return False
            elif any([
                enemy == WeaponType.FIRE and unit in (WeaponType.THUNDER, WeaponType.DARK),
                enemy == WeaponType.THUNDER and unit in (WeaponType.WIND, WeaponType.DARK),
                enemy == WeaponType.WIND and unit in (WeaponType.FIRE, WeaponType.DARK),
                enemy == WeaponType.LIGHT and unit in (WeaponType.THUNDER, WeaponType.FIRE, WeaponType.WIND),
                enemy == WeaponType.DARK and unit == WeaponType.LIGHT
            ]):
                return True
        elif wt_type == WeaponTriangleType.ALL:
            if any([
                unit in (WeaponType.SWORD, WeaponType.TOME) and enemy in (WeaponType.LANCE, WeaponType.HIDDEN),
                unit in (WeaponType.LANCE, WeaponType.HIDDEN) and enemy in (WeaponType.AXE, WeaponType.BOW),
                unit in (WeaponType.AXE, WeaponType.BOW) and enemy in (WeaponType.SWORD, WeaponType.TOME)
            ]):
                return False
            elif any([
                enemy in (WeaponType.SWORD, WeaponType.TOME) and unit in (WeaponType.LANCE, WeaponType.HIDDEN),
                enemy in (WeaponType.LANCE, WeaponType.HIDDEN) and unit in (WeaponType.AXE, WeaponType.BOW),
                enemy in (WeaponType.AXE, WeaponType.BOW) and unit in (WeaponType.SWORD, WeaponType.TOME)
            ]):
                return True
    return None


def weapon_triangle_atk_bonus(game: FireEmblemGame, unit: ActiveUnit, weapon_type: str,
                              opponent: ActiveUnit, opponent_weapon_type: str):
    """
    Calculates the Atk bonus conferred to the given unit via the weapon triangle, based
    on their weapon, their opponent's weapon, and their respective weapon ranks
    :param game: game whose mechanics are to be used for this check
    :param unit: unit to calculate for
    :param weapon_type: type of weapon unit is wielding
    :param opponent: opponent
    :param opponent_weapon_type: type of weapon opponent is wielding
    :return: a bonus to add to Atk. May be negative, or zero.
    """
    wta = weapon_triangle_status(game, weapon_type, opponent_weapon_type)
    if wta is not None:
        try:
            wta_weapon_type = weapon_type if wta else opponent_weapon_type
            wta_weapon_holder = unit if wta else opponent
            wta_bonus = WeaponTriangleBonus.objects.get(
                game=game,
                weapon_rank=ranks.weapon_rank_for_unit(game, wta_weapon_type, wta_weapon_holder)
            ).atk_bonus
            if wta is True:
                return wta_bonus
            else:
                return -wta_bonus
        except ObjectDoesNotExist:
            pass
    return 0


def weapon_triangle_hit_bonus(game: FireEmblemGame, unit: ActiveUnit, weapon_type: str,
                              opponent: ActiveUnit, opponent_weapon_type: str):
    """
    Calculates the Hit bonus conferred to the given unit via the weapon triangle, based
    on their weapon, their opponent's weapon, and their respective weapon ranks
    :param game: game whose mechanics are to be used for this check
    :param unit: unit to calculate for
    :param weapon_type: type of weapon unit is wielding
    :param opponent: opponent
    :param opponent_weapon_type: type of weapon opponent is wielding
    :return: a bonus to add to Hit. May be negative, or zero.
    """
    wta = weapon_triangle_status(game, weapon_type, opponent_weapon_type)
    if wta is not None:
        try:
            wta_weapon_type = weapon_type if wta else opponent_weapon_type
            wta_weapon_holder = unit if wta else opponent
            wta_bonus = WeaponTriangleBonus.objects.get(
                game=game,
                weapon_rank=ranks.weapon_rank_for_unit(game, wta_weapon_type, wta_weapon_holder)
            ).hit_bonus
            if wta is True:
                return wta_bonus
            else:
                return -wta_bonus
        except ObjectDoesNotExist:
            pass
    return 0


def weapon_rank_hit_bonus(game: FireEmblemGame, unit: ActiveUnit, weapon_type: str,
                          opponent_weapon_type: Union[str, None]):
    """
    Calculates the Hit bonus conferred by the unit's weapon rank for the given
    weapon type. If the unit is at Weapon Triangle Disadvantage and the game's
    mechanics nullify the Weapon Rank Bonuses in such a case, returns 0.
    :param game: game whose mechanics to use
    :param unit: unit to calculate Hit bonus for
    :param weapon_type: weapon type that unit is using
    :param opponent_weapon_type: opponent's weapon type for checking WTD
    :return: the Hit bonus conferred by the unit's weapon rank, specifically, if any
    """
    if game.weapon_triangle_suppresses_rank \
            and opponent_weapon_type \
            and weapon_triangle_status(game, weapon_type, opponent_weapon_type) is False:
        return 0
    try:
        return WeaponRankBonus.objects.get(
            game=game,
            weapon_type=weapon_type,
            weapon_rank=ranks.weapon_rank_for_unit(game, weapon_type, unit)
        ).hit_bonus
    except ObjectDoesNotExist:
        return 0


def weapon_rank_atk_bonus(game: FireEmblemGame, unit: ActiveUnit, weapon_type: str,
                          opponent_weapon_type: Union[str, None]):
    """
    Calculates the Atk bonus conferred by the unit's weapon rank for the given
    weapon type. If the unit is at Weapon Triangle Disadvantage and the game's
    mechanics nullify the Weapon Rank Bonuses in such a case, returns 0.
    :param game: game whose mechanics to use
    :param unit: unit to calculate Atk bonus for
    :param weapon_type: weapon type that unit is using
    :param opponent_weapon_type: opponent's weapon type for checking WTD
    :return: The Atk bonus conferred by the unit's weapon rank, specifically, if any
    """
    if game.weapon_triangle_suppresses_rank \
            and opponent_weapon_type \
            and weapon_triangle_status(game, weapon_type, opponent_weapon_type) is False:
        return 0
    try:
        return WeaponRankBonus.objects.get(
            game=game,
            weapon_type=weapon_type,
            weapon_rank=ranks.weapon_rank_for_unit(game, weapon_type, unit)
        ).atk_bonus
    except ObjectDoesNotExist:
        return 0


def weapon_rank_crit_bonus(game: FireEmblemGame, unit: ActiveUnit, weapon_type: str) -> int:
    """
    Calculates the crit bonus conferred by the unit's weapon rank for the given
    weapon type. There is no situation where Weapon Triangle Disadvantage nullifies
    this bonus (the games where that's a thing are not the games that have a crit
    bonus attached), so that's not attempted here.
    :param game: the game whose crit mechanics to use
    :param unit: the unit for which to calculate this
    :param weapon_type: the weapon type in use
    :return: the crit bonus that comes from weapon rank
    """
    try:
        return WeaponRankBonus.objects.get(
            game=game,
            weapon_type=weapon_type,
            weapon_rank=ranks.weapon_rank_for_unit(game, weapon_type, unit)
        ).crit_bonus
    except ObjectDoesNotExist:
        return 0
