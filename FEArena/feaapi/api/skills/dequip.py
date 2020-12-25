from typing import Dict, Callable, Union
from ...models.play.ActiveUnit import ActiveUnit


def _(_: ActiveUnit) -> None:
    pass


def str_plus_five(unit: ActiveUnit) -> None:
    """
    Takes away the str modifier of +5 that was added earlier
    """
    unit.mod_str -= 5


def luk_plus_five(unit: ActiveUnit) -> None:
    """
    Takes away the luk modifier of +5 that was added earlier
    """
    unit.mod_luk -= 5


def def_plus_five(unit: ActiveUnit) -> None:
    """
    Takes away the def modifier of +5 that was added earlier
    """
    unit.mod_def -= 5


def res_plus_five(unit: ActiveUnit) -> None:
    """
    Takes away the res modifier of +5 that was added earlier
    """
    unit.mod_res -= 5


###########################
# FE7-specific skills
###########################


def fe7_uber_spear(unit: ActiveUnit) -> None:
    """
    Removes the following earlier-given bonuses from unit:
    Max HP +17, Str +5, Skl +4, Spd +9, Def +4, Res +14
    """
    unit.mod_max_hp -= 17
    unit.mod_str -= 5
    unit.mod_skl -= 4
    unit.mod_spd -= 9
    unit.mod_def -= 4
    unit.mod_res -= 14


dequip: Dict[Union[str, None], Callable[[ActiveUnit], Union[Dict, None]]] = {
    "str+5": str_plus_five,
    "luk+5": luk_plus_five,
    "def+5": def_plus_five,
    "res+5": res_plus_five,
    "fe7_uber_spear": fe7_uber_spear,
    None: _
}
