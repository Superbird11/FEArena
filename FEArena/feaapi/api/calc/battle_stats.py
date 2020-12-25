"""
File: AS.py

Contains routines to calculate Attack Speed via various different methods
"""
from typing import Union
from . import stats
from . import weapons
from . import support
from ...models.core.Weapon import WeaponType, WeaponDamageType
from ...models.core.Game import FireEmblemGame
from ...models.core.Game import AttackSpeedCalculationMethod as AS_Methods
from ...models.core.Game import HitCalculationMethod as Hit_Methods
from ...models.core.Game import AvoidCalculationMethod as Avoid_Methods
from ...models.core.Game import CritRateCalculationMethod as Crit_Methods
from ...models.core.Game import CritAvoidCalculationMethod as Dodge_Methods
from ...models.core.Game import AttackCalculationMethod as Attack_Methods
from ...models.core.Game import AttackEffectiveDamageCalculationMethod as Eff_Attack_Methods
from ...models.core.Game import AttackEffectiveDamageModifier as Eff_Multiplier
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.play.ActiveArena import ActiveArena


def attack_speed(game: FireEmblemGame, unit: ActiveUnit, weapon: Union[ActiveWeapon, None]) -> int:
    """
    Calculates and returns the unit's Attack Speed, based on the AS calculation method
    of the current game, the unit's stats, the given weapon's Weight. If the weapon
    is None, always returns the unit's base Spd stat
    :param game: game to determine method to use for calculating AS.
    :param unit: unit for which to calculate AS
    :param weapon: Weapon unit is assumed to be holding
    :return: Unit's functional Attack Speed
    """
    method = game.attack_speed_method
    if method == AS_Methods.SPEED or (weapon is None and method != AS_Methods.SPEED_MINUS_WEIGHT_MINUS_STR_OVER_FIVE):
        return stats.calc_spd(unit)
    elif method == AS_Methods.SPEED_MINUS_WEIGHT:
        return stats.calc_spd(unit) - weapon.template.wt
    elif method == AS_Methods.SPEED_MINUS_WEIGHT_MINUS_CON:
        return stats.calc_spd(unit) - max(weapon.template.wt - stats.calc_con(unit), 0)
    elif method == AS_Methods.SPEED_MINUS_WEIGHT_MINUS_CON_BUT_NOT_FOR_MAGIC:
        if weapon.template.weapon_type in (WeaponType.TOME, WeaponType.FIRE, WeaponType.THUNDER, WeaponType.WIND,
                                           WeaponType.DARK, WeaponType.LIGHT, WeaponType.ANIMA, WeaponType.BLACK,
                                           WeaponType.WHITE):
            return stats.calc_spd(unit) - weapon.template.wt
        else:
            return stats.calc_spd(unit) - max(weapon.template.wt - stats.calc_con(unit), 0)
    elif method == AS_Methods.SPEED_MINUS_WEIGHT_MINUS_STR:
        return stats.calc_spd(unit) - max(weapon.template.wt - stats.calc_str(unit), 0)
    elif method == AS_Methods.SPEED_MINUS_WEIGHT_MINUS_STR_OVER_FIVE:
        # this is exclusively the calc method for Three Houses, which allows carried items to have weight
        # if the unit has an equipped item, count that too
        item_wt = 0
        for item in unit.items.all():
            if item.equipped:
                item_wt = item.template.wt
        weapon_wt = weapon.template.wt if weapon else 0
        return stats.calc_spd(unit) - max(weapon_wt + item_wt - stats.calc_str(unit) // 5, 0)
    else:
        raise ValueError(f"Unrecognized AS calculation method '{method}' for game {game.name}")


def hit(arena: ActiveArena, unit: ActiveUnit, weapon: Union[ActiveWeapon, None],
        opponent: ActiveUnit, opponent_weapon_type: Union[str, None]) -> int:
    """
    Calculates the unit's Hit, based on the Hit calculation method of the current
    game, the unit's stats, and their weapon. If weapon is nonexistent, Hit is 0.
    Skills are not accounted for
    :param arena: arena in which fight is taking place
    :param unit: unit for which to calculate Hit
    :param weapon: Weapon unit is assumed to be holding
    :param opponent: opponent ActiveUnit, for WTA calculations
    :param opponent_weapon_type: the opponent's weapon type, for WTA calculations.
    :return: Unit's Hit battle stat
    """
    game = arena.game
    method = game.hit_method
    if weapon is None:
        return 0
    elif method == Hit_Methods.SKL_NOT_MAGIC:
        if weapon.template.damage_type == WeaponDamageType.MAGICAL:
            final_hit = weapon.hit
        else:
            final_hit = stats.calc_skl(unit) + weapon.template.hit
    elif method == Hit_Methods.SKL_TIMES_2:
        final_hit = stats.calc_skl(unit) * 2 + weapon.template.hit
    elif method == Hit_Methods.SKL_TIMES_2_PLUS_LUK:
        final_hit = stats.calc_skl(unit) * 2 + stats.calc_luk(unit) + weapon.template.hit
    elif method == Hit_Methods.SKL_TIMES_2_PLUS_HALF_LUK:
        final_hit = stats.calc_skl(unit) * 2 + stats.calc_luk(unit) // 2 + weapon.template.hit
    elif method == Hit_Methods.SKL_TIMES_2_PLUS_HALF_LUK_PLUS_RANK:
        final_hit = stats.calc_skl(unit) * 2 + stats.calc_luk(unit) // 2 + weapon.template.hit + \
                    weapons.weapon_rank_hit_bonus(game, unit, weapon.template.weapon_type, opponent_weapon_type)
    elif method == Hit_Methods.SKL_PLUS_HALF_LUK_PLUS_RANK:
        final_hit = stats.calc_skl(unit) + stats.calc_luk(unit) // 2 + weapon.template.hit + \
                    weapons.weapon_rank_hit_bonus(game, unit, weapon.template.weapon_type, opponent_weapon_type)
    elif method == Hit_Methods.SKL_TIMES_THREEHALFS_PLUS_HALF_LUK_PLUS_RANK:
        final_hit = (stats.calc_skl(unit) * 1.5 + stats.calc_luk(unit) / 2) // 1 + weapon.template.hit + \
                    weapons.weapon_rank_hit_bonus(game, unit, weapon.template.weapon_type, opponent_weapon_type)
    elif method == Hit_Methods.SKL_OR_HALF_SKL_PLUS_LUK:
        if weapon.template.damage_type == WeaponDamageType.MAGICAL:
            final_hit = weapon.template.hit + (stats.calc_skl(unit) + stats.calc_luk(unit)) // 2
        else:
            final_hit = weapon.template.hit + stats.calc_skl(unit)
    else:
        raise ValueError(f"Unrecognized Hit Calculation Method '{method}' for game {game.name}")
    # calculate weapon triangle factor and apply it, if applicable
    support_bonus = support.hit_boosts(arena, unit)
    if not opponent_weapon_type:
        return support_bonus + final_hit
    return support_bonus + final_hit + weapons.weapon_triangle_hit_bonus(game, unit, weapon.template.weapon_type,
                                                                         opponent, opponent_weapon_type)


def avoid(arena: ActiveArena, unit: ActiveUnit, weapon: Union[ActiveWeapon, None]) -> int:
    """
    Calculates the unit's Avoid, based on the Avoid calculation method of the given
    game, the unit's stats, and their weapon (no skills accounted for, nor terrain)
    :param arena: arena in which combat is taking place
    :param unit: unit for which to calculate Avo
    :param weapon: Weapon unit is assumed to be holding
    :return: Unit's Avoid battle stat
    """
    game = arena.game
    method = game.avoid_method
    support_bonus = support.avo_boosts(arena, unit)
    if method == Avoid_Methods.AS_OR_LUK:
        if weapon and weapon.template.damage_type == WeaponDamageType.MAGICAL:
            return support_bonus + stats.calc_luk(unit)
        else:
            return support_bonus + attack_speed(game, unit, weapon)
    elif method == Avoid_Methods.AS_OR_SPD_PLUS_LUK:
        if weapon and weapon.template.damage_type == WeaponDamageType.MAGICAL:
            return support_bonus + stats.calc_spd(unit) + stats.calc_luk(unit)
        else:
            return support_bonus + attack_speed(game, unit, weapon)
    elif method == Avoid_Methods.SPD_PLUS_LUK:
        return support_bonus + stats.calc_spd(unit) + stats.calc_luk(unit)
    elif method == Avoid_Methods.AS_TIMES_TWO_PLUS_LUK:
        return support_bonus + 2 * attack_speed(game, unit, weapon) + stats.calc_luk(unit)
    elif method == Avoid_Methods.AS_PLUS_HALF_LUCK:
        return support_bonus + attack_speed(game, unit, weapon) + stats.calc_luk(unit) // 2
    elif method == Avoid_Methods.AS_TIMES_THREEHALFS_PLUS_HALF_LUK:
        return support_bonus + int(attack_speed(game, unit, weapon) * 1.5 + stats.calc_luk(unit) / 2)
    elif method == Avoid_Methods.AS_OR_HALF_SPD_PLUS_LUK:
        if weapon and weapon.template.damage_type == WeaponDamageType.MAGICAL:
            return support_bonus + (stats.calc_spd(unit) + stats.calc_luk(unit)) // 2
        else:
            return support_bonus + attack_speed(game, unit, weapon)
    else:
        raise ValueError(f"Unrecognized Avoid Calculation Method '{method}' for game {game.name}")


def crit(arena: ActiveArena, unit: ActiveUnit, weapon: Union[ActiveWeapon, None]) -> int:
    """
    Calculates the unit's Critical Hit Rate, based on the appropriate method of the
    given game, the unit's stats, and their weapon (not accounting for skills).
    If the weapon is None, then crit rate is 0
    :param arena: arena that the fight is taking place in
    :param unit: unit for which to calculate crit
    :param weapon: Weapon unit is assumed to be holding
    :return: Unit's Crit battle stat
    """
    if not weapon:
        return 0
    game = arena.game
    method = game.crit_method
    support_bonus = support.hit_boosts(arena, unit)
    if method == Crit_Methods.HALF_SKILL_PLUS_LUK:
        return support_bonus + weapon.template.crit + (stats.calc_skl(unit) + stats.calc_luk(unit)) // 2
    elif method == Crit_Methods.SKL:
        return support_bonus + weapon.template.crit + stats.calc_skl(unit)
    elif method == Crit_Methods.ZERO:
        return support_bonus
    elif method == Crit_Methods.HALF_SKILL:
        return support_bonus + weapon.template.crit + stats.calc_skl(unit) // 2
    elif method == Crit_Methods.HALF_SKILL_PLUS_RANK:
        return support_bonus + weapon.template.crit + stats.calc_skl(unit) // 2 + \
               weapons.weapon_rank_crit_bonus(game, unit, weapon.template.weapon_type)
    elif method == Crit_Methods.HALF_SKILL_OR_SKILL_MINUS_10:
        skl = stats.calc_skl(unit)
        if skl < 20:
            return support_bonus + weapon.template.crit + skl // 2
        else:
            return support_bonus + weapon.template.crit + skl - 10
    elif method == Crit_Methods.HALF_SKILL_MINUS_FOUR:
        return support_bonus + weapon.template.crit + (stats.calc_skl(unit) - 4) // 2
    else:
        raise ValueError(f"Unrecognized Crit calculation method '{method}' for game {game.name}")


def dodge(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    Calculates the unit's Critical Avoid Rate, based on the appropriate method of the
    given game, the unit's stats, and their weapon (not accounting for skills).
    :param arena: arena that battle is taking place in
    :param unit: unit for which to calculate ddg
    :return: Unit's Ddg battle stat
    """
    game = arena.game
    method = game.crit_avoid_method
    support_bonus = support.ddg_boosts(arena, unit)
    if method == Dodge_Methods.ZERO:
        return support_bonus
    elif method == Dodge_Methods.HALF_LUK:
        return support_bonus + stats.calc_luk(unit) // 2
    elif method == Dodge_Methods.LUK:
        return support_bonus + stats.calc_luk(unit)
    else:
        raise ValueError(f"Unrecognized Crit Avoid calculation method '{method}' for game {game.name}")


def attack(arena: ActiveArena, unit: ActiveUnit, weapon: Union[ActiveWeapon, None],
           opponent: ActiveUnit, opponent_weapon_type: Union[str, None]) -> int:
    """
    Calculates the unit's Attack corresponding to their weapon type. Accounts for
    the unit's stats, WTA, and supports, but does not account for
    skills or effective damage. If unit's weapon is None, returns 0.
    :param arena: arena that the combat is taking place in
    :param unit: unit for which to calculate Atk
    :param weapon: weapon unit is assumed to be wielding
    :param opponent: opponent unit, for calculating WTA or WTD
    :param opponent_weapon_type:  Type of weapon opponent is wielding
    :return: the Atk of the unit with this weapon
    """
    game: FireEmblemGame = arena.game
    if not weapon:
        return 0
    # first, weapon Mt
    final_atk = weapon.template.mt
    # next, add user's appropriate stat
    if weapon.template.damage_type == WeaponDamageType.FIXED:
        return final_atk
    elif weapon.template.damage_type == WeaponDamageType.MAGICAL and game.has_mag_stat:
        final_atk += stats.calc_mag(unit)
    else:
        final_atk += stats.calc_str(unit)
    # apply support boosts if relevant
    final_atk += support.atk_boosts(arena, unit)
    # check game's attack calculation method for other factors
    method = game.attack_method
    if method == Attack_Methods.NO_WEAPON_TRIANGLE:
        return final_atk
    elif method in (Attack_Methods.WEAPON_TRIANGLE, Attack_Methods.WEAPON_TRIANGLE_RANK) and opponent_weapon_type:
        # apply weapon triangle, if applicable
        final_atk += weapons.weapon_triangle_atk_bonus(game, unit, weapon.template.weapon_type,
                                                       opponent, opponent_weapon_type)
    if method == Attack_Methods.WEAPON_TRIANGLE_RANK:
        # apply weapon rank bonus as well
        final_atk += weapons.weapon_rank_atk_bonus(game, unit, weapon.template.weapon_type, opponent_weapon_type)
    return final_atk


def attack_effective(arena: ActiveArena, unit: ActiveUnit, weapon: Union[ActiveWeapon, None],
                     opponent: ActiveUnit, opponent_weapon_type: Union[str, None], mod: Union[int, None]) -> int:
    """
    Calculates the unit's Attack corresponding to their weapon type, assuming this attack
    deals effective damage against the opponent. Accounts for
    the unit's stats and weapon triangle advantage, but does not account for
    skills. If unit's weapon is None, returns 0.
    :param arena: arena in which combat is taking place
    :param unit: unit for which to calculate Atk
    :param weapon: weapon unit is assumed to be wielding
    :param opponent: opponent unit, for calculating WTA or WTD
    :param opponent_weapon_type:  Type of weapon opponent is wielding
    :param mod: if the effective damage varies based on skills, then use this modifier
    :return: the Atk of the unit with this weapon
    """
    game = arena.game
    if not weapon:
        return 0
    eff_mod = game.attack_effective_mod
    if eff_mod == Eff_Multiplier.SKILL_DEPENDENT:
        eff_mod = mod
    # first, weapon Mt
    mt = weapon.template.mt
    if game.attack_effective_method in (
            Eff_Attack_Methods.MT_EFFECTIVE, Eff_Attack_Methods.MT_WT_EFFECTIVE, Eff_Attack_Methods.DMG_EFFECTIVE
    ):
        mt *= eff_mod
    # next, add user's appropriate stat
    if weapon.template.damage_type == WeaponDamageType.FIXED:
        return mt
    elif weapon.template.damage_type == WeaponDamageType.MAGICAL and game.has_mag_stat:
        stat = stats.calc_mag(unit)
    else:
        stat = stats.calc_str(unit)
    if game.attack_effective_method == Eff_Attack_Methods.DMG_EFFECTIVE:
        stat *= eff_mod
    # apply support bonus if relevant, _after_ effective weapon damage modification
    support_bonus = support.atk_boosts(arena, unit)
    # check game's attack calculation method for other factors
    method = game.attack_method
    # apply weapon triangle, if applicable
    if method == Attack_Methods.NO_WEAPON_TRIANGLE:
        return mt + stat + support_bonus
    elif method in (Attack_Methods.WEAPON_TRIANGLE, Attack_Methods.WEAPON_TRIANGLE_RANK) and opponent_weapon_type:
        wt_bonus = weapons.weapon_triangle_atk_bonus(game, unit, weapon.template.weapon_type,
                                                     opponent, opponent_weapon_type)
    else:
        wt_bonus = 0
    if game.attack_effective_method == Eff_Attack_Methods.MT_WT_EFFECTIVE:
        wt_bonus *= eff_mod
    # apply weapon rank bonus if applicable
    if method == Attack_Methods.WEAPON_TRIANGLE_RANK:
        rank = weapons.weapon_rank_atk_bonus(game, unit, weapon.template.weapon_type, opponent_weapon_type)
    else:
        rank = 0
    return mt + stat + wt_bonus + rank + support_bonus


def protection(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    Calculates the unit's Protection against physical attacks. This will almost
    always be equal to their effective defense stat, and the weapon has no bearing
    on it.
    :param arena: arena in which combat is taking place
    :param unit: unit to calculate Prt for
    :return: the Prt of the unit
    """
    return stats.calc_def(unit) + support.prt_rsl_boosts(arena, unit)


def resilience(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    Calculate the unit's Resilience against magical attacks. This will usually
    be equal to the unit's Res, or in the case of Thracia 776, their Mag.
    :param arena: arena in which combat is taking place
    :param unit: unit for which to calculate Rsl
    :return: the Rsl of the unit
    """
    support_bonus = support.prt_rsl_boosts(arena, unit)
    if arena.game.use_mag_as_res:
        return stats.calc_mag(unit) + support_bonus
    return stats.calc_res(unit) + support_bonus


def prt_or_rsl(damage_type: str, prt: int, rsl: int) -> int:
    """
    Depending on the given damage type, returns Prt or Rsl respectively,
    whichever is more appropriate
    :param damage_type: The DamageType being dealt
    :param prt: a unit's Prt
    :param rsl: a unit's Rsl
    :return: whichever of Prt and Rsl is relevant to the weapon, or 0
        if the weapon deals fixed damage
    """
    if damage_type == WeaponDamageType.PHYSICAL:
        return prt
    elif damage_type == WeaponDamageType.MAGICAL:
        return rsl
    else:  # self.attacker_weapon.template.damage_type == WeaponDamageType.FIXED:
        return 0
