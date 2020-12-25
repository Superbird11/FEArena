from typing import Dict, Callable, Union
import random
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.SkillData import SkillData


def _(_: ActiveArena, __: ActiveUnit) -> None:
    pass


def fe7_poisoned(arena: ActiveArena, unit: ActiveUnit) -> Union[Dict, None]:
    """
    Deducts a random amount of HP (1-5) from the unit, and decreases death counter.
    If poison wears off, does not return anything.
    """
    fe7_poisoned_skill = unit.temp_skills.get(id=701)  # TODO change when I know fe7_poisoned's ID
    skill_data: SkillData = SkillData.objects.get(arena=arena, unit=unit, skill=fe7_poisoned_skill)
    hp_to_deduct = random.randint(1, 5)
    skill_data.data_int1 -= 1
    if skill_data.data_int1 <= 0:
        # remove skill and delete skill data
        skill_data.delete()
        unit.temp_skills.remove(skill_data)
    else:
        unit.current_hp -= hp_to_deduct
        skill_data.save()
        # don't save unit; caller will do that eventually
        return {
            "action": "activate_skill",
            "skill": "fe7_poisoned",
            "data": hp_to_deduct,
            "show": True
        }


turn_start: Dict[Union[str, None], Callable[[ActiveArena, ActiveUnit], Union[Dict, None]]] = {
    "fe7_poisoned": fe7_poisoned,
    None: _
}
