from ..build.BuiltUnit import BuiltUnit
from ..build.BuiltTeam import BuiltTeam
from .ActiveUnit import ActiveUnit
from .ActiveItem import ActiveItem
from .ActiveWeapon import ActiveWeapon
from .ActiveTeam import ActiveTeam
from ...api import skills
from ...api.calc import stats


def ActiveUnit_from_BuiltUnit(built_unit: BuiltUnit):
    """
    Creates and saves an ActiveUnit object and all component parts.
    :param built_unit: unit template to copy, for building this active unit. It is expected
                       that this built_unit has already been saved to database.
    """
    # assign unit and template
    unit = ActiveUnit.objects.create(template=built_unit)
    # create weapons and items, and invoke 'equip' skills for the weapons equipped at creation
    # ignore summaries, since this is creation-time
    for weapon in unit.template.weapons.all():
        unit.weapons.add(ActiveWeapon.from_BuiltWeapon(weapon))
        if weapon.equipped:
            skills.equip_all(weapon.template.weapon_effects.all(), unit)
    for item in unit.template.items.all():
        unit.items.add(ActiveItem.from_BuiltItem(item))
        if item.equipped:
            skills.equip_all(item.template.weapon_effects.all(), unit)
    # apply passive skills
    for skill in skills.accumulate(
            personal=built_unit.unit,
            unit_class=built_unit.unit_class,
            active_weapons=unit.weapons.all(),
            active_items=unit.items.all(),
            extra=built_unit.extra_skills.all(),
    ):
        if skill.passive_effect:
            skills.passive[skill.passive_effect](unit)
    # calculate current HP manually from max HP (max_hp mod may have been altered)
    unit.current_hp = stats.calc_max_hp(unit)
    # save and return unit
    unit.save()
    return unit


def ActiveTeam_from_BuiltTeam(built_team: BuiltTeam):
    """
    Creates and saves an ActiveTeam object and all component parts.
    :param built_team: team template to copy, for building this active team. It is expected
                       that this built_team has already been saved to database.
    """
    # safety check to make using this method more straightforward for ActiveArena
    if built_team is None:
        return None
    # actually assign important attributes
    team = ActiveTeam.objects.create(template=built_team)
    for built_unit in built_team.units.all():
        team.units.add(ActiveUnit_from_BuiltUnit(built_unit))
    team.save()
    return team
