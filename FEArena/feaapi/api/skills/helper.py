from typing import Iterable as Iterable, List, Dict, Callable, Iterator, Set, Optional
from ...models.core.Unit import Unit
from ...models.core.Class import Class
from ...models.core.Weapon import Weapon
from ...models.core.Item import Item
from ...models.core.Skill import Skill
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.play.ActiveItem import ActiveItem
from ...models.build.BuiltUnit import BuiltUnit
from ..calc.combat_data import AttackData, AfterAttackData
from ..calc.combat import CombatData
from .passive import passive
from .dequip import dequip
from .equip import equip
from .use import use
from .before_attack import before_attack
from .after_attack import after_attack
from .before_attacked import before_attacked
from .after_attacked import after_attacked
from .before_combat import before_combat
from .after_combat import after_combat
from .turn_start import turn_start
from .turn_end import turn_end
from .unit_turn_end import unit_turn_end
from .on_build import on_build


def _interleave_by_priority(skill_getter1: Callable[[Skill], Callable],
                            skills1: Iterable[Skill], args1: Iterable,
                            skill_getter2: Callable[[Skill], Callable],
                            skills2: Iterable[Skill], args2: Iterable) -> List[Dict]:
    """
    Executes the skills in order of priority, providing the given arguments to each skill call
    according to which set it comes from.
    :param skill_getter1: a lambda to return the correct skill implementation given a skill, for unit1
    :param skill_getter2: a lambda to return the correct skill implementation given a skill, for unit2
    :param skills1: first set of skills to execute
    :param args1: arguments to give when calling first set of skills
    :param skills2: second set of skills to execute
    :param args2: arguments to give when calling second set of skills
    :return: a list of standard skill outputs conforming to the appropriate subschema
        (see api.arena.schemas)
    """
    skills1 = iter(sorted(skills1, key=lambda skl: -skl.priority))
    skills2 = iter(sorted(skills2, key=lambda skl: -skl.priority))
    try:
        sk1 = next(skills1)
    except StopIteration:
        return list(filter(_exists, (skill_getter2(s)(*args2) for s in skills2)))
    try:
        sk2 = next(skills2)
    except StopIteration:
        return list(filter(_exists, (skill_getter1(s)(*args1) for s in (sk1, *skills1))))
    output = []
    while True:
        if sk2.priority > sk1.priority:
            skill_output = skill_getter2(sk2)(*args2)
            if skill_output:
                output.append(skill_output)
            try:
                sk2 = next(skills2)
            except StopIteration:
                return output + list(filter(_exists, (skill_getter1(s)(*args1) for s in (sk1, *skills1))))
        else:
            skill_output = skill_getter1(sk1)(*args1)
            if skill_output:
                output.append(skill_output)
            try:
                sk1 = next(skills1)
            except StopIteration:
                return output + list(filter(_exists, (skill_getter2(s)(*args2) for s in (sk2, *skills2))))


def accumulate(
        personal: Unit = None,
        unit_class: Class = None,
        weapons: Iterable[Weapon] = None,
        active_weapons: Iterable[ActiveWeapon] = None,
        items: Iterable[Item] = None,
        active_items: Iterable[ActiveItem] = None,
        extra: Iterable[Skill] = None
) -> Iterator[Skill]:
    """
    A generator that chains the skill lists of all prospective sources of skills, yielding one at a time.
    :param personal: A single Unit whose personal skills are to be accumulated
    :param unit_class: A Class, presumably belonging to the unit, whose class skills are to be accumulated
    :param weapons: an iterable containing Weapon objects to accumulate the skills from
    :param active_weapons: An iterable containing ActiveWeapon objects to accumulate the skills from
    :param items: an iterable containing Item objects to accumulate the skills from
    :param active_items: An iterable containing ActiveItem objects to accumulate the skills from
    :param extra: an iterable containing extra skills (probably from a BuiltUnit)
    :return: a generator that yields skills one at a time from all given sources
    """
    # personal, class, and extra skills
    if personal:
        yield from personal.personal_skills.all()
    if unit_class:
        yield from unit_class.class_skills.all()
    if extra:
        yield from extra
    # weapons and active weapons
    if weapons:
        for weapon in weapons:
            yield from weapon.weapon_effects.all()
    if active_weapons:
        for active_weapon in active_weapons:
            yield from active_weapon.template.weapon_effects.all()
    # items and active items
    if items:
        for item in items:
            yield from item.item_effects.all()
    if active_items:
        for active_item in active_items:
            yield from active_item.template.item_effects.all()


def _exists(obj: any) -> bool:
    return bool(obj)


def passive_all(skills: Iterable[Skill], unit: ActiveUnit) -> None:
    """
    Executes the passive_effect for all the given skills, if such exists. Passive skills
    do not have output.
    :param skills: an iterable containing Skills whose passive_effects are to be executed
    :param unit: the argument to give to the passive_effect skill execution
    """
    for s in skills:
        passive[s.passive_effect](unit)


def dequip_all(skills: Iterable[Skill], unit: ActiveUnit) -> List[Dict]:
    """
    Executes the on_dequip_effect for all the given skills, if such exists, returning a list of their
    cumulative output, if applicable
    :param skills: an iterable containing Skills whose on_dequip_effects are to be executed
    :param unit: the argument to give to the on_dequip_effect execution
    :return: a list of dequip() outputs, conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (dequip[s.on_dequip_effect](unit) for s in skills)))


def equip_all(skills: Iterable[Skill], unit: ActiveUnit) -> List[Dict]:
    """
    Executes the on_equip_effect for all the given skills, if such exists, returning a list of their
    cumulative output, if applicable
    :param skills: an iterable containing Skills whose on_equip_effects are to be executed
    :param unit: the argument to give to the on_equip_effect execution
    :return: a list of equip() outputs, conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (equip[s.on_equip_effect](unit) for s in skills)))


def use_all(skills: Iterable[Skill], arena: ActiveArena, unit: ActiveUnit,
            target: Optional[ActiveUnit], extra_data: Optional[str]) -> List[Dict]:
    """
    Executes the on_use_effect for all the given skills, if such exists, returning a list of their
    cumulative output, if applicable
    :param skills: an iterable containing Skills whose on_equip_effects are to be executed
    :param arena: the arena in which the battle is currently being fought
    :param unit: the argument to give to the on_equip_effect execution
    :param target: optionally, the target for the skill
    :param extra_data: extra data required for the skill to be used
    :return: a list of use() outputs, conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (use[s.on_use_effect](arena, unit, target, extra_data) for s in skills)))


def before_attack_all(skills: Iterable[Skill], data: AttackData) -> List[Dict]:
    """
    Executes the before_attack_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose before_attack_effects are to be executed
    :param data: the AttackData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (before_attack[s.before_attack_effect](data) for s in skills)))


def before_attacked_all(skills: Iterable[Skill], data: AttackData) -> List[Dict]:
    """
    Executes the before_attacked_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose before_attacked_effects are to be executed
    :param data: the AttackData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (before_attacked[s.before_attacked_effect](data) for s in skills)))


def before_attack_with_priority(attacker: Iterable[Skill], attacked: Iterable[Skill], data: AttackData) -> List[Dict]:
    """
    Executes the before_attack_effect or before_attacked_effect, respectively
    :param attacker: iterable of skills on which to execute before_attack_effect
    :param attacked: iterable of skills on which to execute before_attacked_effect
    :param data: argument to pass to skill calls
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return _interleave_by_priority(lambda s: before_attack[s.before_attack_effect],
                                   attacker, [data],
                                   lambda s: before_attacked[s.before_attacked_effect],
                                   attacked, [data])


def after_attack_all(skills: Iterable[Skill], arena: ActiveArena, data: AfterAttackData) -> List[Dict]:
    """
    Executes the after_attack_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose after_attack_effects are to be executed
    :param arena: the ActiveArena being fought in, for adding temporary skills if necessary
    :param data: the AfterAttackData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (after_attack[s.after_attack_effect](arena, data) for s in skills)))


def after_attacked_all(skills: Iterable[Skill], data: AfterAttackData) -> List[Dict]:
    """
    Executes the after_attacked_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose after_attacked_effects are to be executed
    :param data: the AfterAttackData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (after_attacked[s.after_attacked_effect](data) for s in skills)))


def before_combat_all(skills: Iterable[Skill], unit: ActiveUnit, arena: ActiveArena, data: CombatData) -> List[Dict]:
    """
    Executes the before_combat_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose before_combat_effect are to be executed
    :param unit: the unit to whom these skills belong
    :param arena: the ActiveArena the battle is taking place in
    :param data: the CombatData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (before_combat[s.before_combat_effect](unit, arena, data) for s in skills)))


def before_combat_with_priority(skills1: Iterable[Skill], unit1: ActiveUnit,
                                skills2: Iterable[Skill], unit2: ActiveUnit,
                                arena: ActiveArena, data: CombatData) -> List[Dict]:
    """
    Executes the before_combat_effect for all given skills, such that they are executed in order
    of priority between the two combatants
    :param skills1: The list of skills to execute before_combat_effect for that belong to unit1
    :param unit1: the unit who the skills1 belong to
    :param skills2: the list of skills to execute before_combat_effect for that belong to unit2
    :param unit2: the unit who skills2 belong to
    :param arena: the ActiveArena the battle is taking place in
    :param data: the CombatData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return _interleave_by_priority(lambda s: before_combat[s.before_combat_effect],
                                   skills1, [unit1, arena, data],
                                   lambda s: before_combat[s.before_combat_effect],
                                   skills2, [unit2, arena, data])


def after_combat_all(skills: Iterable[Skill], unit: ActiveUnit, arena: ActiveArena, data: CombatData) -> List[Dict]:
    """
    Executes the after_combat_effect for all the given skills, if such exists, returning a list
    of their cumulative output, if applicable
    :param skills: an iterable containing Skills whose after_combat_effect are to be executed
    :param unit: the unit to whom these skills belong
    :param arena: the ActiveArena the battle is taking place in
    :param data: the CombatData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return list(filter(_exists, (after_combat[s.after_combat_effect](unit, arena, data) for s in skills)))


def after_combat_with_priority(skills1: Iterable[Skill], unit1: ActiveUnit,
                               skills2: Iterable[Skill], unit2: ActiveUnit,
                               arena: ActiveArena, data: CombatData) -> List[Dict]:
    """
    Executes the after_combat_effect for all given skills, such that they are executed in order
    of priority between the two combatants
    :param skills1: The list of skills to execute after_combat_effect for that belong to unit1
    :param unit1: the unit who the skills1 belong to
    :param skills2: the list of skills to execute after_combat_effect for that belong to unit2
    :param unit2: the unit who skills2 belong to
    :param arena: the ActiveArena the battle is taking place in
    :param data: the CombatData to feed to the skill functions
    :return: a list of outputs conforming to the appropriate subschema in api.arena.schemas
    """
    return _interleave_by_priority(lambda s: after_combat[s.after_combat_effect],
                                   skills1, [unit1, arena, data],
                                   lambda s: after_combat[s.after_combat_effect],
                                   skills2, [unit2, arena, data])


def turn_start_all(skills: Iterable[Skill], unit: ActiveUnit, arena: ActiveArena) -> List[Dict]:
    """
    Executes the turn_start_effect for all given skills, if such exists, returning a
    list of their cumulative output
    :param skills: skills to use
    :param unit: the unit to whom the skills belong
    :param arena: the ActiveArena the battle is taking place in
    :return: a list of outputs to append to the existing list of actions, conforming to api.arena.schemas
    """
    return list(filter(_exists, (turn_start[s.turn_start_effect](arena, unit) for s in skills)))


def turn_end_all(skills: Iterable[Skill], unit: ActiveUnit, arena: ActiveArena) -> List[Dict]:
    """
    Executes the turn_end_effect for all given skills, if such exists, returning a
    list of their cumulative output
    :param skills: skills to use
    :param unit: the unit to whom the skills belong
    :param arena: the ActiveArena the battle is taking place in
    :return: a list of outputs to append to the existing list of actions, conforming to api.arena.schemas
    """
    return list(filter(_exists, (turn_end[s.turn_end_effect](arena, unit) for s in skills)))


def unit_turn_end_all(skills: Iterable[Skill], unit: ActiveUnit, arena: ActiveArena, actions: List[Dict]) -> List[Dict]:
    """
    Executes the unit_turn_end_effect for all given skills, if such exists, returning a
    list of their cumulative output
    :param skills: skills to use
    :param unit: the unit to whom the skills belong
    :param arena: the ActiveArena the battle is taking place in
    :param actions: the actions (conforming to api.arena.schemas) that have been taken so far this turn
    :return: a list of outputs to append to the existing list of actions, conforming to api.arena.schemas
    """
    return list(filter(_exists, (unit_turn_end[s.unit_turn_end_effect](arena, unit, actions) for s in skills)))


def on_build_all(skills: Iterable[Skill], unit: BuiltUnit, av_skills: Set[Skill]):
    """
    Executes the build effect for all given skills, if such exists. Does not return anything, because
    on_build skills don't need to.
    :param skills: skills to use
    :param unit: the unit to whom the skills belong
    :param av_skills: A Set of available skills to the unit, possibly to be added to. `unit.extra_skills`
         should not be directly modified by any of these; instead, skills added to av_skills.
    """
    return list(filter(_exists, (on_build[s.build_effect](unit, av_skills) for s in skills)))


__all__ = ['accumulate', 'passive_all', 'dequip_all', 'equip_all', 'use_all', 'before_attack_all', 'after_attack_all',
           'before_attacked_all', 'after_attacked_all', 'before_combat_all', 'after_combat_all',
           'turn_start_all', 'turn_end_all', 'unit_turn_end_all', 'on_build_all',
           'before_attack_with_priority', 'before_combat_with_priority', 'after_combat_with_priority']
