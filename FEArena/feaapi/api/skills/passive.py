from typing import Dict, Callable, Union
from ...models.core.Skill import Skill
from ...models.play.ActiveUnit import ActiveUnit


def _(_: ActiveUnit) -> None:
    pass


def fe7_delphi_shield(unit: ActiveUnit) -> None:
    """
    Gives the unit the temporary skill with ID 1, which should prevent effective-against-flying
    weapons from dealing effective damage
    """
    anti_flying_weakness = Skill.objects.get(id=1)
    unit.temp_skills.add(anti_flying_weakness)


# Passive skills are invoked at unit-creation-time, and do not return any summaries
passive: Dict[Union[str, None], Callable[[ActiveUnit], None]] = {
    "delphi_shield": fe7_delphi_shield,
    None: _
}
