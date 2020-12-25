from typing import Dict, Callable, Union
from ...models.core.Weapon import Weapon
from ...models.core.Skill import Skill
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveArena import ActiveArena
from ...models.play.SkillData import SkillData
from ..calc.combat import CombatData
from ..calc import stats, battle_stats, weapons


def _(___: ActiveUnit, _: ActiveArena, __: CombatData) -> None:
    pass


###########################
# Skills common to various games
###########################

def crit_plus15(unit: ActiveUnit, _: ActiveArena, combat: CombatData) -> None:
    """
    Gives the unit a flat 15-point increase to their Crit battle-stat
    """
    if combat.attacker == unit:
        combat.set_crit_attacker(combat.crit_attacker + 15)
    elif combat.defender == unit:
        combat.set_crit_defender(combat.crit_defender + 15)
    return None


def effective_cavalry(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent is a cavalry unit, then this unit's attacks deal effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.cavalry\
            and combat.defender.temp_skills.filter(id=2).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.cavalry\
            and combat.attacker.temp_skills.filter(id=2).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def effective_armored(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent is an armored unit, then this unit's attacks deal effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.armored\
            and combat.defender.temp_skills.filter(id=3).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.armored\
            and combat.attacker.temp_skills.filter(id=3).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def effective_flying(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent is an armored unit, then this unit's attacks deal effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.flying \
            and combat.defender.temp_skills.filter(id=1).count() == 0:  # nullifies Flying weakness if present
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.flying \
            and combat.attacker.temp_skills.filter(id=1).count() == 0:  # nullifies Flying weakness it present:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def effective_dragons(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent is a dragon, then this unit's attacks deal effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.dragon\
            and combat.defender.temp_skills.filter(id=4).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.dragon\
            and combat.attacker.temp_skills.filter(id=4).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def effective_wyverns(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent is a dragon, then this unit's attacks deal effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.wyvern\
            and combat.defender.temp_skills.filter(id=5).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.wyvern\
            and combat.attacker.temp_skills.filter(id=5).count() == 0:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


###########################
# FE7-specific skills
###########################

def fe7_reverse_weapon_triangle(_: ActiveArena, arena: ActiveArena, combat: CombatData) -> None:
    """
    Apply the reverse of the current weapon triangle boost to all factors affected by it,
    including by the other combatant.
    """
    # Calculate weapon triangle boosts for the attacker, but assign them to the defender
    # and vice versa
    # This should negate itself if applied twice, once by each combatant.
    defender_wt_atk = weapons.weapon_triangle_atk_bonus(arena.game,
                                                        combat.attacker, combat.attacker_weapon.template.weapon_type,
                                                        combat.defender, combat.defender_weapon.template.weapon_type)
    defender_wt_hit = weapons.weapon_triangle_hit_bonus(arena.game,
                                                        combat.attacker, combat.attacker_weapon.template.weapon_type,
                                                        combat.defender, combat.defender_weapon.template.weapon_type)
    attacker_wt_atk = weapons.weapon_triangle_atk_bonus(arena.game,
                                                        combat.defender, combat.defender_weapon.template.weapon_type,
                                                        combat.attacker, combat.attacker_weapon.template.weapon_type)
    attacker_wt_hit = weapons.weapon_triangle_hit_bonus(arena.game,
                                                        combat.defender, combat.defender_weapon.template.weapon_type,
                                                        combat.attacker, combat.attacker_weapon.template.weapon_type)
    # The reaver weapons double the effects of the weapon triangle. To offset the initial one,
    # which has already been applied, we need to multiply our change by 3 instead of 2
    combat.set_atk_attacker(combat.atk_attacker + 3 * attacker_wt_atk)
    combat.set_hit_attacker(combat.hit_attacker + 3 * attacker_wt_hit)
    combat.set_atk_defender(combat.atk_defender + 3 * defender_wt_atk)
    combat.set_hit_defender(combat.hit_defender + 3 * defender_wt_hit)
    return None


def fe7_siege_weapon(unit: ActiveUnit, _: ActiveArena, combat: CombatData) -> None:
    """
    If triggered by the attacker, prevents the defender from counterattacking but restricts
    the attacker to just one hit. If triggered by the defender, prevents them from
    counterattacking at all.
    """
    if unit == combat.attacker:
        while combat.attack_data and combat.attack_data.by != unit:
            combat.attack_data = combat.attack_data.next
        if combat.attack_data:
            combat.attack_data.next = None
    elif unit == combat.defender:
        while combat.attack_data and combat.attack_data.by == unit:
            combat.attack_data = combat.attack_data.next
        if combat.attack_data:
            for ad in combat.attack_data:
                while ad.next and ad.next.by == unit:
                    ad.next = ad.next.next


def fe7_swordslayer(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent's class uses mainly swords, deals effective damage
    """
    sword_class_names = ['Myrmidon', 'Swordmaster', 'Mercenary', 'Hero', 'Blade Lord']
    if combat.attacker == unit and combat.defender.template.unit_class.name in sword_class_names:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.name in sword_class_names:
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def fe7_effective_dark_druid(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> Dict:
    """
    If the unit's opponent's class is Dark Druid, deals effective damage
    """
    if combat.attacker == unit and combat.defender.template.unit_class.name == 'Dark Druid':
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.attacker,
            weapon=combat.attacker_weapon,
            opponent=combat.defender,
            opponent_weapon_type=combat.defender_weapon.template.weapon_type if combat.defender_weapon else None,
            mod=None
        )
        combat.set_atk_attacker(new_atk)
    elif combat.defender == unit and combat.attacker.template.unit_class.name == 'Dark Druid':
        new_atk = battle_stats.attack_effective(
            arena=arena,
            unit=combat.defender,
            weapon=combat.defender_weapon,
            opponent=combat.attacker,
            opponent_weapon_type=combat.attacker_weapon.template.weapon_type,
            mod=None
        )
        combat.set_atk_defender(new_atk)
    return {"action": "effective_attacks", "unit": unit.id}


def fe7_iron_rune(unit: ActiveUnit, _: ActiveArena, combat: CombatData) -> None:
    """
    Increases the unit's Ddg battle-stat by 999. Note that displayed crit doesn't go below 0.
    """
    if combat.attacker == unit:
        combat.set_ddg_attacker(999)
    elif combat.defender == unit:
        combat.set_ddg_defender(999)


def fe7_light_brand(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> None:
    """
    If unit is fighting from greater than 1-range, replaces the unit's weapon and magic stat
    such that the resulting attack is magical and the attack strength is the unit's str / 2.
    Will reset these properties at the end of combat.
    """
    if combat.range > 1:
        light_brand = Weapon.objects.get(id=714)
        light_brand_skill = Skill.objects.get(id=709)
        if combat.attacker == unit:
            # save information about unit's prior state
            prev_weapon_id = combat.attacker_weapon.template.id
            prev_mag_mod = unit.mod_mag
            SkillData.objects.create(
                game=arena.game,
                unit=unit,
                skill=light_brand_skill,
                data_int1=prev_weapon_id,
                data_int2=prev_mag_mod,
            )
            # replace current weapon and stats
            new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
            combat.attacker_weapon.template = light_brand
            combat.attacker.mod_mag -= new_mod_mag
            combat.recalculate_from_weapon_changes()
        elif combat.defender == unit:
            # save information about unit's prior state
            prev_weapon_id = combat.defender_weapon.template.id
            prev_mag_mod = unit.mod_mag
            SkillData.objects.create(
                game=arena.game,
                unit=unit,
                skill=light_brand_skill,
                data_int1=prev_weapon_id,
                data_int2=prev_mag_mod,
            )
            # replace current weapon and stats
            new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
            combat.defender_weapon.template = light_brand
            combat.defender.mod_mag -= new_mod_mag
            combat.recalculate_from_weapon_changes()
    return None


def fe7_wind_edge(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> None:
    """
    If unit is fighting from greater than 1-range, replaces the unit's weapon and magic stat
    such that the resulting attack is magical and the attack strength is the unit's str / 2.
    Will reset these properties at the end of combat.
    """
    if combat.range > 1:
        wind_edge = Weapon.objects.get(id=718)
        wind_edge_skill = Skill.objects.get(id=710)
        if combat.attacker == unit:
            # save information about unit's prior state
            prev_weapon_id = combat.attacker_weapon.template.id
            prev_mag_mod = unit.mod_mag
            SkillData.objects.create(
                game=arena.game,
                unit=unit,
                skill=wind_edge_skill,
                data_int1=prev_weapon_id,
                data_int2=prev_mag_mod,
            )
            # replace current weapon and stats
            new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
            combat.attacker_weapon.template = wind_edge
            combat.attacker.mod_mag -= new_mod_mag
            combat.recalculate_from_weapon_changes()
        elif combat.defender == unit:
            # save information about unit's prior state
            prev_weapon_id = combat.defender_weapon.template.id
            prev_mag_mod = unit.mod_mag
            SkillData.objects.create(
                game=arena.game,
                unit=unit,
                skill=wind_edge_skill,
                data_int1=prev_weapon_id,
                data_int2=prev_mag_mod,
            )
            # replace current weapon and stats
            new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
            combat.defender_weapon.template = wind_edge
            combat.defender.mod_mag -= new_mod_mag
            combat.recalculate_from_weapon_changes()
    return None


def fe7_runesword(unit: ActiveUnit, arena: ActiveArena, combat: CombatData) -> None:
    """
    Replaces the unit's magic stat such that the resulting value equals the unit's str / 2.
    In FE7 and FE8, the Runesword is always magical, so no weapon-swap necessary.
    Will reset the user's magic modifier at the end of combat.
    """
    runesword = Weapon.objects.get(id=722)
    runesword_skill = Skill.objects.get(id=711)
    if combat.attacker == unit:
        # save information about unit's prior state
        prev_weapon_id = combat.attacker_weapon.template.id
        prev_mag_mod = unit.mod_mag
        SkillData.objects.create(
            game=arena.game,
            unit=unit,
            skill=runesword_skill,
            data_int1=prev_weapon_id,
            data_int2=prev_mag_mod,
        )
        # replace current weapon and stats
        new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
        combat.attacker_weapon.template = runesword
        combat.attacker.mod_mag -= new_mod_mag
        combat.recalculate_from_weapon_changes()
        # also, attacker cannot crit with this weapon in FE7
        combat.set_crit_attacker(-999)
    elif combat.defender == unit:
        # save information about unit's prior state
        prev_mag_mod = unit.mod_mag
        prev_weapon_id = combat.defender_weapon.template.id
        SkillData.objects.create(
            game=arena.game,
            unit=unit,
            skill=runesword_skill,
            data_int1=prev_weapon_id,
            data_int2=prev_mag_mod,
        )
        # replace current weapon and stats
        new_mod_mag = (stats.calc_str(unit) // 2) - stats.calc_mag(unit)
        combat.defender_weapon.template = runesword
        combat.defender.mod_mag -= new_mod_mag
        combat.recalculate_from_weapon_changes()
        # also, the user of this weapon cannot crit with it in FE7
        combat.set_crit_defender(-999)
    return None


def fe7_luna(unit: ActiveUnit, _: ActiveArena, combat: CombatData) -> None:
    """
    Makes the opponent's Rsl to be zero for the purposes of this combat
    """
    if combat.attacker == unit:
        combat.set_rsl_defender(0)
    elif combat.defender == unit:
        combat.set_rsl_attacker(0)


def fe7_eclipse(unit: ActiveUnit, _: ActiveArena, combat: CombatData) -> None:
    """
    Sets the damage such that the opponent takes damage equal to half their current HP,
    rounded up. Also, has zero crit rate.
    """
    if unit == combat.attacker:
        combat.set_atk_attacker((combat.defender.current_hp + 1) // 2)
        combat.set_rsl_defender(0)
        combat.set_crit_attacker(-999)
    elif unit == combat.defender:
        combat.set_atk_defender((combat.attacker.current_hp + 1) // 2)
        combat.set_rsl_attacker(0)
        combat.set_crit_defender(-999)


before_combat: Dict[Union[str, None], Callable[[ActiveUnit, ActiveArena, CombatData], Union[Dict, None]]] = {
    'effective_cavalry': effective_cavalry,
    'effective_armored': effective_armored,
    'effective_flying': effective_flying,
    'effective_dragons': effective_dragons,
    'effective_wyverns': effective_wyverns,
    'crit+15': crit_plus15,
    'fe7_reverse_weapon_triangle': fe7_reverse_weapon_triangle,
    'fe7_siege_weapon': fe7_siege_weapon,
    'fe7_swordslayer': fe7_swordslayer,
    'fe7_dark_druid': fe7_effective_dark_druid,
    'iron_rune': fe7_iron_rune,
    'fe7_light_brand': fe7_light_brand,
    'fe7_runesword': fe7_runesword,
    'fe7_wind_edge': fe7_wind_edge,
    'fe7_luna': fe7_luna,
    'fe7_eclipse': fe7_eclipse,
    None: _
}
