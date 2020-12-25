from typing import Dict, Callable, Union, Set
from ...models.build.BuiltUnit import BuiltUnit
from ...models.core.Skill import Skill


def _(_: BuiltUnit, __: Set[Skill]) -> None:
    pass


def all_growths_plus5(unit: BuiltUnit, skillset: Set[Skill]) -> None:
    """
    Applies boosts to the BuiltUnit equal to the number of extra stat points the Afa's Drops
    would have allowed the unit to get, if applied immediately.
    This applies to Str, Mag, Skl, Spd, Luk, Def, and Res, but not Con, Mov, or Cha
    """
    total_levels = sum(bc.levels for bc in unit.unit_class_history)
    normal_hp_growths = unit.unit.base_hp + unit.unit_class.base_hp + unit.unit.growth_hp * total_levels + \
        sum(bc.template.growth_hp * bc.levels for bc in unit.unit_class_history)
    unit.boosts_hp += (normal_hp_growths + 5 * total_levels) // 100 - normal_hp_growths // 100
    
    normal_str_growths = unit.unit.base_str + unit.unit_class.base_str + unit.unit.growth_str * total_levels + \
        sum(bc.template.growth_str * bc.levels for bc in unit.unit_class_history)
    unit.boosts_str += (normal_str_growths + 5 * total_levels) // 100 - normal_str_growths // 100

    normal_mag_growths = unit.unit.base_mag + unit.unit_class.base_mag + unit.unit.growth_mag * total_levels + \
        sum(bc.template.growth_mag * bc.levels for bc in unit.unit_class_history)
    unit.boosts_mag += (normal_mag_growths + 5 * total_levels) // 100 - normal_mag_growths // 100

    normal_skl_growths = unit.unit.base_skl + unit.unit_class.base_skl + unit.unit.growth_skl * total_levels + \
        sum(bc.template.growth_skl * bc.levels for bc in unit.unit_class_history)
    unit.boosts_skl += (normal_skl_growths + 5 * total_levels) // 100 - normal_skl_growths // 100

    normal_spd_growths = unit.unit.base_spd + unit.unit_class.base_spd + unit.unit.growth_spd * total_levels + \
        sum(bc.template.growth_spd * bc.levels for bc in unit.unit_class_history)
    unit.boosts_spd += (normal_spd_growths + 5 * total_levels) // 100 - normal_spd_growths // 100

    normal_luk_growths = unit.unit.base_luk + unit.unit_class.base_luk + unit.unit.growth_luk * total_levels + \
        sum(bc.template.growth_luk * bc.levels for bc in unit.unit_class_history)
    unit.boosts_luk += (normal_luk_growths + 5 * total_levels) // 100 - normal_luk_growths // 100

    normal_def_growths = unit.unit.base_def + unit.unit_class.base_def + unit.unit.growth_def * total_levels + \
        sum(bc.template.growth_def * bc.levels for bc in unit.unit_class_history)
    unit.boosts_def += (normal_def_growths + 5 * total_levels) // 100 - normal_def_growths // 100

    normal_res_growths = unit.unit.base_res + unit.unit_class.base_res + unit.unit.growth_res * total_levels + \
        sum(bc.template.growth_res * bc.levels for bc in unit.unit_class_history)
    unit.boosts_res += (normal_res_growths + 5 * total_levels) // 100 - normal_res_growths // 100
    return None


# on-build skills modify the BuiltUnit and their set of available extra skills
on_build: Dict[Union[str, None], Callable[[BuiltUnit, Set[Skill]], None]] = {
    "growths+5": all_growths_plus5,
    None: _
}
