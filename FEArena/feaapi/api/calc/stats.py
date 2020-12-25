"""
file: stats.py

Contains methods for calculating the final stat values of ActiveUnits.
"""

from ...models.play.ActiveUnit import ActiveUnit


def calc_max_hp(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Max HP stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Max HP
    :return: the unit's current Max HP stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_hp
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_hp * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_hp for cls in class_history)
    boosts_hp = unit.template.boosts_hp
    max_hp = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts_hp
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_hp_cap = unit.template.unit.max_hp if unit.template.unit.max_hp >= 0 else max_hp
    class_hp_cap = unit.template.unit_class.max_hp + unit.template.unit.mod_max_hp
    if class_hp_cap < 0:
        class_hp_cap = max_hp
    final_value = min(max_hp, unit_hp_cap, class_hp_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_max_hp
    return final_value


def calc_str(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Strength stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Str
    :return: the unit's current Str stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_str
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_str * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_str for cls in class_history)
    boosts = unit.template.boosts_str
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_str if unit.template.unit.max_str >= 0 else stat_max
    class_cap = unit.template.unit_class.max_str + unit.template.unit.mod_max_str
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_str
    return final_value


def calc_mag(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Magic stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Mag
    :return: the unit's current Mag stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_mag
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_mag * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_mag for cls in class_history)
    boosts = unit.template.boosts_mag
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_mag if unit.template.unit.max_mag >= 0 else stat_max
    class_cap = unit.template.unit_class.max_mag + unit.template.unit.mod_max_mag
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_mag
    return final_value


def calc_spd(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Speed stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Spd
    :return: the unit's current Spd stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_spd
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_spd * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_spd for cls in class_history)
    boosts = unit.template.boosts_spd
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_spd if unit.template.unit.max_spd >= 0 else stat_max
    class_cap = unit.template.unit_class.max_spd + unit.template.unit.mod_max_spd
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_spd
    return final_value


def calc_skl(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Skill/Dexterity stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Skl/Dex
    :return: the unit's current Skl/Dex stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_skl
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_skl * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_skl for cls in class_history)
    boosts = unit.template.boosts_skl
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_skl if unit.template.unit.max_skl >= 0 else stat_max
    class_cap = unit.template.unit_class.max_skl + unit.template.unit.mod_max_skl
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_skl
    return final_value


def calc_luk(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Luck stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Luk
    :return: the unit's current Luk stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_luk
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_luk * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_luk for cls in class_history)
    boosts = unit.template.boosts_luk
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_luk if unit.template.unit.max_luk >= 0 else stat_max
    class_cap = unit.template.unit_class.max_luk + unit.template.unit.mod_max_luk
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_luk
    return final_value


def calc_def(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Defense stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Def
    :return: the unit's current Def stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_def
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_def * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_def for cls in class_history)
    boosts = unit.template.boosts_def
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_def if unit.template.unit.max_def >= 0 else stat_max
    class_cap = unit.template.unit_class.max_def + unit.template.unit.mod_max_def
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_def
    return final_value


def calc_res(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Resistance stat by adding together unit bases,
    class bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Res
    :return: the unit's current Res stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_res
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_res * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_res for cls in class_history)
    boosts = unit.template.boosts_res
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_res if unit.template.unit.max_res >= 0 else stat_max
    class_cap = unit.template.unit_class.max_res + unit.template.unit.mod_max_res
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_res
    return final_value


def calc_cha(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Charm stat by adding together
     unit bases, lass bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Cha
    :return: the unit's current Cha stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_cha
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_cha * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_cha for cls in class_history)
    boosts = unit.template.boosts_cha
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_cha if unit.template.unit.max_cha >= 0 else stat_max
    class_cap = unit.template.unit_class.max_cha + unit.template.unit.mod_max_cha
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_cha
    return final_value


def calc_mov(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Movement stat by adding together
     unit bases, lass bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Mov
    :return: the unit's current Mov stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_mov
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_mov * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_mov for cls in class_history)
    boosts = unit.template.boosts_mov
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_mov if unit.template.unit.max_mov >= 0 else stat_max
    class_cap = unit.template.unit_class.max_mov + unit.template.unit.mod_max_mov
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_mov
    return final_value


def calc_con(unit: ActiveUnit) -> int:
    """
    Calculates the given ActiveUnit's Constitution/Build stat by adding together
     unit bases, lass bases, growths from each, current bonuses, and stat caps.
    :param unit: unit for which to calculate Con/Bld
    :return: the unit's current Con/Bld stat
    """
    class_history = unit.template.unit_class_history.all()
    # add unit and class bases together
    unit_base = unit.template.unit.base_con
    class_base = unit.template.unit_class.base_hp
    # calculate number of stat points earned from growths (divided by 100) and bonuses
    unit_growths = unit.template.unit.growth_con * sum(cls.levels for cls in class_history)
    class_growths = sum(cls.levels * cls.template.growth_con for cls in class_history)
    boosts = unit.template.boosts_con
    stat_max = unit_base + class_base + (unit_growths + class_growths) // 100 + boosts
    # if stat would exceed unit or class caps, decrease it accordingly.
    # Either unit cap or class cap will probably be -1, but probably not both
    unit_cap = unit.template.unit.max_con if unit.template.unit.max_con >= 0 else stat_max
    class_cap = unit.template.unit_class.max_con + unit.template.unit.mod_max_con
    if class_cap < 0:
        class_cap = stat_max
    final_value = min(stat_max, unit_cap, class_cap)
    # apply current transient boosts/reductions
    final_value += unit.mod_con
    return final_value
