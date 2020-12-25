"""
file: teambuilder/validator.py

Validates changes to BuiltUnits, based on the mechanics of a particular game, raising
a ValueError whenever a validation fails.
"""
from django.core.exceptions import ObjectDoesNotExist
from typing import Iterable, List, Dict, Set, Iterator
from ...models.build.BuiltUnit import BuiltUnit
from ...models.build.RankedSupport import RankedSupport
from ...models.core.RankedSupportTemplate import RankedSupportTemplate
from ...models.core.WeaponRank import WeaponRank
from ...models.core.Class import Class
from ...models.core.Unit import Unit, Affinity
from ...models.core.Skill import Skill
from ...models.core.Game import FireEmblemGame, ClassChangeEligibility, SkillLimit, FireEmblemGameRoute, AffinityTypes
from ..calc import ranks


def validate_unit_routes(do: bool, units: List[BuiltUnit]):
    """
    Validation fails if at least two units are obtained from mutually-exclusive routes.
    Validation also fails if the same unit is included twice (i.e. their (game, name) tuples are identical)
    """
    if not do:
        return
    routes: List[FireEmblemGameRoute] = list(set(unit.unit.route for unit in units if unit.unit.route))
    for i in range(len(routes) - 1):
        for j in range(i+1, len(routes)):
            if j in routes[i].mutually_exclusive.all() or j in routes[i].mutually_exclusive.all():
                raise ValueError(f"Units from routes {routes[i].name} and {routes[j].name} ({routes[i].game}) may not"
                                 f"be used together on the same team")
    for i in range(len(units) - 1):
        for j in range(1, len(units)):
            if (units[i].unit.game, units[i].unit.name) == (units[j].unit.game, units[j].unit.name):
                raise ValueError(f"The same unit ({units[i].unit.name} from {units[i].unit.game.abbrev}) cannot"
                                 f"be on the team twice, even if recruitable in multiple places")


def validate_level_up(do: bool, unit: BuiltUnit):
    """
    Validation fails if the given unit is already at max level.
    """
    if not do:
        return
    if unit.unit_level == unit.unit_class.maximum_level:
        raise ValueError(f"Unit cannot level up past level {unit.unit_level} in class {unit.unit_class.name}")


def validate_boost_weapon_rank(do: bool, game: FireEmblemGame, unit: BuiltUnit, weapon_type: str):
    """
    Validation fails if unit does not have at least E rank in the given weapon type,
    accounting for class
    """
    if not do:
        return
    if ranks.weapon_rank_for_built_unit(game, weapon_type, unit) <= WeaponRank.NONE:
        raise ValueError(f"Unit cannot use weapon type {weapon_type}")


def validate_promotion(do: bool, unit: BuiltUnit, current_class: Class, new_class: Class):
    """
    Validation fails if the current_class cannot naturally promote into the new_class,
    or if the unit is not at a sufficient level for promotion
    """
    if not do:
        return
    if unit.unit_level < current_class.minimum_promotion_level:
        raise ValueError(f"Level {unit.unit_level} is too low for unit to promote out of class {current_class.name}")
    if new_class not in current_class.promotes_to.all():
        raise ValueError(f"Unit in class {current_class.name} ({current_class.game.abbrev}) cannot promote to"
                         f" {new_class.name} ({new_class.game.abbrev}")


def validate_class_change(do: bool, game: FireEmblemGame, unit: BuiltUnit, current_class: Class, new_class: Class):
    """
    Validation fails if the new class is not a natural progression from the unit's class set,
    as well as if specific level benchmarks are not hit
    """
    if not do:
        return
    # check eligibility for class change first
    method = game.class_change_allowed
    if method == ClassChangeEligibility.NO:
        raise ValueError(f"Game {game.name} does not allow units to class change")
    elif method == ClassChangeEligibility.ABLE_TO_PROMOTE:
        # This is specifically written for Awakening's leveling mechanics, hence the constant 20
        # for classes like Manakete that level to 40, and start counting as an advanced class at 30
        if new_class.promoted:
            if not current_class.promoted and unit.unit_level < current_class.minimum_promotion_level + 20:
                raise ValueError(f"Level {unit.unit_level} is too low for unit to change class from "
                                 f"{current_class.name} to {new_class.name}")
            elif current_class.promoted and unit.unit_level < current_class.minimum_promotion_level:
                raise ValueError(f"Level {unit.unit_level} is too low for unit to change class from "
                                 f"{current_class.name} to {new_class.name}")
        else:
            if not current_class.promoted and unit.unit_level < current_class.minimum_promotion_level:
                raise ValueError(f"Level {unit.unit_level} is too low for unit to change class from "
                                 f"{current_class.name} to {new_class.name}")
    elif method == ClassChangeEligibility.MINIMUM_PROMOTION_LEVEL:
        # This is specifically written for Three houses's mechanics - instead of using Minimum Promotion Level
        # for its intended purpose, since you're there already by classing in and thus can class out at any time,
        # we use it to tell how high-level you have to be to class into the class. We will ignore weapon ranks
        # for now.
        if unit.unit_level < new_class.minimum_promotion_level:
            raise ValueError(f"Level {unit.unit_level} is too low for unit to change class into {new_class.name}")
    # check that class is part of unit's available class set
    # (for Three Houses, every available class for the unit should be in their individual class set)
    if new_class != unit.unit.initial_class and new_class not in promotion_tree(unit.unit.base_classes):
        raise ValueError(f"New class {new_class.name} is not in unit {unit.unit.name}'s class set")


def validate_inventory(do: bool, game: FireEmblemGame, inventory: List[Dict]):
    """
    Validation fails if the inventory exceeds the game's limits in total size,
    or if it contains more weapons and/or items than the game allows of either
    """
    if not do:
        return
    # check game's total inventory limit
    if len(inventory) > game.max_inventory_size:
        raise ValueError(f"Too much equipment ({len(inventory)}) for {game.abbrev}'s "
                         f"inventory size ({game.max_inventory_size})")
    if len([item for item in inventory if item['kind'] == 'item']) > game.max_inventory_items:
        raise ValueError(f"Inventory in {game.abbrev} can only contain at most {game.max_inventory_items} items")
    if len([weapon for weapon in inventory if weapon['kind'] == 'weapon']) > game.max_inventory_weapons:
        raise ValueError(f"Inventory in {game.abbrev} can only contain at most {game.max_inventory_weapons} weapons")


def validate_extra_skills(do: bool, game: FireEmblemGame, unit: BuiltUnit,
                          possible_skills: Set[Skill], extra_skills: List[Skill]):
    """
    Validation fails if the number of extra skills exceeds the unit/game's limit (depending on
    game's mechanics), or if any of the extra skills is not in the set of possible skills
    """
    if not do:
        return
    # check skill limits
    method = game.extra_skills_limit
    if method == SkillLimit.QUANTITY and len(extra_skills) > game.extra_skills_quantity_limit:
        raise ValueError(f"{game.name} limits units to at most {game.extra_skills_quantity_limit} extra skills")
    elif method == SkillLimit.UNIT_TOLERANCE and sum(skl.cost for skl in extra_skills) > unit.unit.skill_tolerance:
        raise ValueError(f"Unit {unit.unit.name}'s skill tolerance is too low for this set of chosen skills")
    # check that skills have, in fact, been earned
    for extra_skill in extra_skills:
        if extra_skill not in possible_skills:
            raise ValueError(f"Unit cannot ever have learned skill {extra_skill.name}")


def validate_support(do: bool, game: FireEmblemGame, unit: BuiltUnit, supported_by: Unit, quantity=1):
    """
    Validation fails if the two units cannot support with each other, if their support
    rank would exceed the game's maximum between any two units, or if THIS UNIT already
    has the game's maximum number of supports
    """
    if not do:
        return
    # check that units can support each other
    if unit.unit.can_ranked_support.filter(id=supported_by.id).count() == 0:
        raise ValueError(f"Unit {unit.unit.name} cannot support unit {supported_by.name}")
    unit_supports = RankedSupport.objects.filter(unit=unit)
    if 0 <= game.support_rank_limit <= sum(rs.rank for rs in unit_supports) + quantity - 1:
        raise ValueError(f"Unit has too many supports")
    try:
        existing_support = unit_supports.get(supported_by=supported_by)
        if existing_support.rank >= game.max_support_rank:
            raise ValueError(f"Units {unit.unit.name} and {supported_by.name} already have the highest possible "
                             f"support rank")
        support_template: RankedSupportTemplate = RankedSupportTemplate.objects.get(unit=unit,
                                                                                    supported_by=supported_by)
        if existing_support.rank >= support_template.max_rank:
            raise ValueError(f"Units {unit.unit.name} and {supported_by.name} already have the highest possible "
                             f"support rank")
    except ObjectDoesNotExist:
        pass


def validate_support_combinations(do: bool, built_units: List[BuiltUnit]):
    """
    Validation fails if any unit has a support with a unit that isn't part of the given list of
    units
    """
    if not do:
        return
    units = [bu.unit for bu in built_units]
    for bu in built_units:
        for support in RankedSupport.objects.filter(unit=bu):
            if support.supported_by not in units:
                raise ValueError(f"{bu.unit.name} is supported by unit {support.supported_by.name}, who is not on"
                                 f"this team")


def validate_tactician(do: bool, game: FireEmblemGame, rank: int, affinity: str):
    """
    Validation fails if rank is lower than 0 or higher than 10,
    or if the given affinity type does not exist in the given game
    """
    if not do:
        return
    aff_method = game.affinity_types
    if aff_method == AffinityTypes.NONE and affinity:
        raise ValueError(f"Game {game.abbrev} does not have affinities in it")
    elif aff_method == AffinityTypes.GBA and affinity in [Affinity.EARTH, Affinity.WATER, Affinity.HEAVEN]:
        raise ValueError(f"The GBA games' affinity system does not include Earth, Water, or Heaven affinities")
    elif aff_method == AffinityTypes.TELLIUS and affinity in [Affinity.ICE, Affinity.ANIMA]:
        raise ValueError(f"The Tellius games' affinity system does not include Ice or Anima affinities")
    if not 0 <= rank <= 10:
        raise ValueError(f"Tactician rank must be between 0 and 10, inclusive")


def promotion_tree(classes: Iterable[Class]) -> Iterator[Class]:
    """
    A generator that outputs a breadth-first search of possible promotions from the given
    list of classes
    :param classes: the base classes to start from
    :return: a generator that outputs all possible class trees starting from the given class
    """
    queue: List[Class] = list(classes)
    i = 0
    while i < len(queue):
        yield queue[i]
        for pc in queue[i].promotes_to.all():
            if pc not in queue:
                queue.append(pc)
        i += 1



