from typing import Dict, Callable, Union
from ...models.core.Skill import Skill
from ...models.play.SkillData import SkillData
from ...models.play.ActiveArena import ActiveArena
from ..calc.combat_data import AfterAttackData
from ..calc import stats


def _(_: ActiveArena, __: AfterAttackData) -> None:
    pass


def fe7_poison_on_hit(arena: ActiveArena, aad: AfterAttackData) -> Union[Dict, None]:
    """
    If the attack hit, poisons the target by giving them the skill `fe7_poisoned`.
    If this triggers, returns the appropriate activate_skill subschema instance
    """
    if not aad.miss:
        fe7_poisoned_skill = Skill.objects.get(id=701)  # TODO change after deciding skill id
        if fe7_poisoned_skill not in aad.against.temp_skills.all():
            aad.against.temp_skills.add(Skill.objects.get(id=701))
            SkillData.objects.add(arena=arena, unit=aad.against, skill=fe7_poisoned_skill, data_int1=5)
        else:
            skill_data = SkillData.objects.get(arena=arena, unit=aad.against, skill=fe7_poisoned_skill)
            skill_data.data_int1 = 5
            skill_data.save()
        return {
            "action": "activate_skill",
            "skill": "fe7_poison",
            "data": aad.against.id,
            "show": True,
        }
    return None


def fe7_nosferatu(arena: ActiveArena, aad: AfterAttackData) -> Union[Dict, None]:
    """
    If the attack dealt damage, restore HP to the user equal to the damage dealt.
    In that case, return a summary conforming to the "restore_health" subschema.
    """
    if aad.dmg > 0:
        health_to_restore = min(aad.dmg, stats.calc_max_hp(aad.by) - aad.by.current_hp)
        aad.by.current_hp += health_to_restore
        return {
            "action": "restore_health",
            "unit": aad.by.id,
            "health": health_to_restore
        }
    return None


after_attack: Dict[Union[str, None], Callable[[ActiveArena, AfterAttackData], Union[Dict, None]]] = {
    'fe7_poison_on_hit': fe7_poison_on_hit,
    'fe7_nosferatu': fe7_nosferatu,
    None: _
}
