from typing import Dict, Callable, Union
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveArena import ActiveArena
from ...models.play.SkillData import SkillData
from ...models.core.Skill import Skill
from ...models.core.Weapon import Weapon
from ..calc.combat import CombatData


def _(___: ActiveUnit, _: ActiveArena, __: CombatData) -> None:
    pass


###########################
# FE7-specific skills
###########################

def fe7_light_brand(unit: ActiveUnit, arena: ActiveArena, combat: CombatData):
    """
    Replaces the unit's Mag modifier and weapon template with their original values
    """
    skill: Skill = Skill.objects.get(id=709)
    skill_data: SkillData = SkillData.objects.get(arena=arena, unit=unit, skill=skill)
    unit.mod_mag = skill_data.data_int2
    if combat.attacker == unit:
        combat.attacker_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    elif combat.defender == unit:
        combat.defender_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    skill_data.delete()


def fe7_wind_edge(unit: ActiveUnit, arena: ActiveArena, combat: CombatData):
    """
    Replaces the unit's Mag modifier and weapon template with their original values
    """
    skill: Skill = Skill.objects.get(id=710)
    skill_data: SkillData = SkillData.objects.get(arena=arena, unit=unit, skill=skill)
    unit.mod_mag = skill_data.data_int2
    if combat.attacker == unit:
        combat.attacker_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    elif combat.defender == unit:
        combat.defender_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    skill_data.delete()


def fe7_runesword(unit: ActiveUnit, arena: ActiveArena, combat: CombatData):
    """
    Replaces the unit's Mag modifier with its initial value.
    """
    skill: Skill = Skill.objects.get(id=711)
    skill_data: SkillData = SkillData.objects.get(arena=arena, unit=unit, skill=skill)
    unit.mod_mag = skill_data.data_int2
    if combat.attacker == unit:
        combat.attacker_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    elif combat.defender == unit:
        combat.defender_weapon.template = Weapon.objects.get(id=skill_data.data_int1)
    skill_data.delete()


def fe7_silencer(unit: ActiveUnit, arena: ActiveArena, combat: CombatData):
    """
    If the unit triggered Silencer as the last attack in this combat,
    double the points/EXP earned from the fight.
    """
    last_attack = next(attack for attack in combat.attack_data if not attack.next)
    if last_attack.by == unit and 'silencer' in last_attack.tags and last_attack.against.current_hp <= 0:
        if combat.attacker == unit:
            combat.attacker_points += combat.defender.template.unit_level * \
                                      combat.defender.template.unit_class.class_strength
        elif combat.defender == unit:
            combat.defender_points *= combat.attacker.template.unit_level * \
                                      combat.attacker.template.unit_class.class_strength


after_combat: Dict[Union[str, None], Callable[[ActiveUnit, ActiveArena, CombatData], Union[Dict, None]]] = {
    'fe7_silencer': fe7_silencer,
    'fe7_light_brand': fe7_light_brand,
    'fe7_wind_edge': fe7_wind_edge,
    'fe7_runesword': fe7_runesword,
    None: _
}
