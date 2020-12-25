from django.core.exceptions import ObjectDoesNotExist
import logging
from typing import List, Dict, Union, Optional
from ..calc import ranks
from ..calc import combat
from ..calc import combat_data
from .. import skills
from ...models.core.Game import WeaponBreakBehavior, FireEmblemGame
from ...models.core.Skill import Skill
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.play.ActiveItem import ActiveItem
from .helper import *


# def validate_order(action_list: List[str]):
#     """
#     Checks that the given list of actions can be performed in their order, and throws a ValueError
#     containing information about the out-of-order action, if not.
#
#     Currently, the only real rule is that 'equip_weapon' and 'equip_item' may not come after
#     'attack' or 'use_*'
#     :param action_list: a list of action names, as enumerated in the action_input_schema
#     """
#     equips_ok = True
#     for action in action_list:
#         if action in ['attack', 'use_weapon', 'use_item', 'use_skill']:
#             equips_ok = False
#         elif not equips_ok and action in ['equip_weapon', 'equip_item', 'discard_weapon', 'discard_item']:
#             raise ValueError(f"Weapons and items may not be equipped after using another action")


def execute_action(arena: ActiveArena, unit: ActiveUnit, act: Dict) -> List[Dict]:
    """
    Based on the type of `act`, executes the given action.
    Returns a summary of the action's effects, conforming to the action_output_schema.
    Mutates the given arena and/or unit and/or their respective derived objects, in the
    course of executing the action.
    :param arena: an ActiveArena representing the entire scope of the current fight
    :param unit: the particular ActiveUnit performing the action
    :param act: the action being performed, conforming to any one of the allowed actions
        defined in the action_input_schema (see api.arena.schemas)
    :return: a list of each sub-action's effects, conforming to the format defined in the
        action_output_schema (See api.arena.schemas)
    """
    # validate
    restricted_actions = unit.restricted_actions.split(',')
    if act['action'] in restricted_actions:
        raise ValueError(f"Unit is not allowed to perform action '{act['action']}' right now")
    if act['action'] == 'equip_weapon':
        return equip_weapon(arena.game, unit, act['weapon'])
    elif act['action'] == 'equip_item':
        return equip_item(unit, act['item'])
    elif act['action'] == 'attack':
        return attack(arena, unit, act['target'], act['with_weapon'], act['range'])
    elif act['action'] == 'use_weapon':
        return use_weapon(arena, unit, act['weapon'], act.get('target', None), act.get('extra_data', None))
    elif act['action'] == 'use_item':
        return use_item(arena, unit, act['item'], act.get('target', None), act.get('extra_data', None))
    elif act['action'] == 'use_skill':
        return use_skill(arena, unit, act['skill'], act.get('target', None), act.get('extra_data', None))
    elif act['action'] == 'discard_weapon':
        return discard_weapon(arena.game, unit, act['weapon'])
    elif act['action'] == 'discard_item':
        return discard_item(unit, act['item'])
    elif act['action'] == 'wait':
        return wait(arena)
    else:
        raise ValueError(f"'{act['action']}' is not a valid action")


def wait(arena: ActiveArena) -> List[Dict]:
    """
    Makes the unit wait. This does nothing other than end the turn, and trigger
    any skills that activate on unit-turn-end.
    :return: a wait action, conforming to the 'wait' subschema in api.arena.schemas
    """
    arena.turn_should_end = True
    return [{"action": "wait"}]


def equip_weapon(game: FireEmblemGame, unit: ActiveUnit, weapon_id: int) -> List[Dict]:
    """
    Equips the weapon with the given weapon_id to the unit, if possible, triggering its effects
    on equip. If the unit does not have the weapon, the unit cannot use the weapon, or the
    weapon does not exist, raises a ValueError.
    :param game: The Fire Emblem game whose mechanics should be used for weapon level considerations
    :param unit: unit to which to equip weapon
    :param weapon_id: id of weapon to equip
    :return: a summary of the equip_weapon action's effects, conforming to the format defined
        in the action_output_schema (see api.arena.schemas)
    """
    # validate
    try:
        weapon: ActiveWeapon = ActiveWeapon.objects.get(id=weapon_id)
    except ObjectDoesNotExist:
        raise ValueError(f"The weapon with id {weapon_id} does not exist!")
    if weapon not in unit.weapons.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding weapon with id {weapon_id}")
    if not ranks.unit_can_equip_weapon(game, unit, weapon):
        raise ValueError(f"The active unit {unit.template.nickname}'s weapon rank is insufficient to equip the"
                         f" weapon {weapon.template.name} (rank {weapon.template.rank}")
    # unequip unit's other weapons, and equip this one
    output = []
    equipped_weapons = unit.weapons.filter(equipped=True)
    for equipped_weapon in equipped_weapons.all():
        equipped_weapon.equipped = False
        equipped_weapon.save()
        output.append({"action": "unequip_weapon", "unit": unit.id, "weapon": equipped_weapon.id})
        output += skills.dequip_all(equipped_weapon.template.weapon_effects.all(), unit)
    weapon.equipped = True
    weapon.save()
    output.append({"action": "equip_weapon", "unit": unit.id, "weapon": weapon_id})
    output += skills.equip_all(weapon.template.weapon_effects.all(), unit)
    # swap item inventory ids, as applicable
    output += shift_weapon_to_front_of_inventory(weapon, unit)
    return output


def equip_item(unit: ActiveUnit, item_id: int) -> List[Dict]:
    """
    Equips the item with the given item_id to the unit, if possible, triggering its effects
    on equip. If the unit does not have the item, the item isn't equippable, or the item
    does not exist, raises a ValueError.
    :param unit: unit to which to equip item
    :param item_id: id of weapon to equip
    :return: a summary of the equip_weapon action's effects, conforming to the format defined
        in the action_output_schema (see api.arena.schemas)
    """
    # validate
    try:
        item: ActiveItem = ActiveItem.objects.get(id=item_id)
    except ObjectDoesNotExist:
        raise ValueError(f"The item with id {item_id} does not exist!")
    if item not in unit.items.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding the item with id {item_id}")
    if item.template.prf_users.count and unit not in item.template.prf_users.all():
        raise ValueError(f"The active unit {unit.template.nickname} cannot equip the Prf item {item.template.name}")
    if not item.template.equippable:
        raise ValueError(f"The item {item.template.name} is not equippable")
    # unequip unit's other items, and equip this one
    output = []
    equipped_items = unit.items.filter(equipped=True)
    for equipped_item in equipped_items.all():
        equipped_item.equipped = False
        equipped_item.save()
        output.append({"action": "unequip_item", "unit": unit.id, "item": equipped_item.id})
        output += skills.dequip_all(equipped_item.template.weapon_effects.all(), unit)
    item.equipped = True
    item.save()
    output.append({"action": "equip_weapon", "unit": unit.id, "weapon": item_id})
    output += skills.equip_all(item.template.item_effects.all(), unit)
    # swap item inventory ids, as applicable
    output += shift_item_to_front_of_inventory(item, unit)
    return output


def use_weapon(arena: ActiveArena, unit: ActiveUnit, weapon_id: int,
               target_id: Optional[int], extra_data: Optional[str]) -> List[Dict]:
    """
    Uses the weapon with the given weapon_id, triggering its on_use effect and reducing
    its durability by one accordingly. If the unit does not have the weapon, the weapon isn't
    usable, or the weapon does not exist, raises a ValueError.
    :param arena: the ActiveArena the battle is taking place in. The weapon's effects may
        reach beyond just the unit.
    :param unit: the ActiveUnit using the item
    :param weapon_id: the id of the ActiveWeapon to use
    :param target_id: if provided, a target for this usage
    :param extra_data: if provided, extra data for this skill to use
    :return: a summary of the use_weapon action's effects, conforming to the format defined
        in the action_output_schema (See api.arena.schemas)
    """
    # validate
    try:
        weapon: ActiveWeapon = ActiveWeapon.objects.get(id=weapon_id)
    except ObjectDoesNotExist:
        raise ValueError(f"The weapon with id {weapon_id} does not exist!")
    if weapon not in unit.weapons.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding weapon with id {weapon_id}")
    if not ranks.unit_can_equip_weapon(arena.game, unit, weapon):
        raise ValueError(f"The active unit {unit.template.nickname}'s weapon rank is insufficient to equip the"
                         f" weapon {weapon.template.name} (rank {weapon.template.rank}")
    if not weapon.template.usable:
        raise ValueError(f"The weapon {weapon.template.name} cannot be used with the 'use' command")
    if target_id is not None:
        try:
            target = ActiveUnit.objects.get(id=target_id)
        except ObjectDoesNotExist:
            raise ValueError(f"The weapon {weapon.template.name}'s target unit {target_id} does not exist")
        # validate using team_containing_unit()
        arena.team_containing_unit(target)
    else:
        target = None
    # use item and decrease durability if possible
    output = list(skills.use_all(weapon.template.weapon_effects.all(), arena, unit, target, extra_data))
    if weapon.uses > 0:
        weapon.uses -= 1
        output.append({"action": "change_weapon_uses", "weapon_id": weapon.id, "new_uses": weapon.uses})
    # break weapon if uses fall to zero
    if weapon.uses == 0:
        if weapon.template.game.on_weapon_break == WeaponBreakBehavior.BREAK and weapon.template.breaks_into:
            weapon.template = weapon.template.breaks_into
            weapon.uses = weapon.template.uses
            output.append({
                "action": "replace_weapon",
                "weapon": weapon.id,
                "new_data": weapon.to_dict()
            })
        else:  # weapon.template.game.on_weapon_break == WeaponBreakBehavior.REMOVE, or fallover
            output += discard_weapon(arena.game, unit, weapon)
    arena.turn_should_end = True
    return output


def use_item(arena: ActiveArena, unit: ActiveUnit, item_id: int,
             target_id: Optional[int], extra_data: Optional[str]) -> List[Dict]:
    """
    Uses the weapon with the given weapon_id, triggering its on_use effect and reducing
    its durability by one accordingly. If the unit does not have the weapon, the weapon isn't
    usable, or the weapon does not exist, raises a ValueError.
    :param arena: the ActiveArena the battle is taking place in. The weapon's effects may
        reach beyond just the unit.
    :param unit: the ActiveUnit using the item
    :param item_id: the id of the ActiveWeapon to use
    :param target_id: if applicable, the target on which to use item
    :param extra_data: if applicable, extra data to send with the skill
    :return: a summary of the use_weapon action's effects, conforming to the format defined
        in the action_output_schema (See api.arena.schemas)
    """
    # validate
    try:
        item: ActiveItem = ActiveItem.objects.get(id=item_id)
    except ObjectDoesNotExist:
        raise ValueError(f"The item with id {item_id} does not exist!")
    if item not in unit.items.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding the item with id {item_id}")
    if item.template.prf_users.count and unit not in item.template.prf_users.all():
        raise ValueError(f"The active unit {unit.template.nickname} cannot use the Prf item {item.template.name}")
    if not item.template.usable:
        raise ValueError(f"The item {item.template.name} is not usable")
    if target_id is not None:
        try:
            target = ActiveUnit.objects.get(id=target_id)
        except ObjectDoesNotExist:
            raise ValueError(f"The item {item.template.name}'s target unit {target_id} does not exist")
        # validate using team_containing_unit()
        arena.team_containing_unit(target)
    else:
        target = None
    # use item and decrease durability if possible
    output = list(skills.use_all(item.template.item_effects.all(), arena, unit, target, extra_data))
    if item.uses > 0:
        item.uses -= 1
        output.append({"action": "change_item_uses", "weapon_id": item.id, "new_uses": item.uses})
    # break weapon if uses fall to zero
    if item.uses == 0:
        # in all Fire Emblem games, items are removed upon death, not broken
        output += discard_item(unit, item.id)
    arena.turn_should_end = True
    return output


def use_skill(arena: ActiveArena, unit: ActiveUnit, skill_id: int,
              target_id: Optional[int], extra_data: Optional[str]) -> List[Dict]:
    """
    If the unit has the given skill, triggers its on_use effect. If the unit does not
    have the skill as a personal, class, or extra skill (weapon and item skills should
    be triggered by those weapons/items only), or if the skill has no on_use_effect,
    raises a ValueError.
    :param arena: the ActiveArena the battle is taking place in
    :param unit: the ActiveUnit using the item
    :param skill_id: the skill to be used
    :param target_id: if applicable, the unit on which to use the skill
    :param extra_data: if applicable, extra data to pass for the skill
    :return: a summary of the skill's effects, conforming to the format defined in the
        action_output_schema (see api.arena.schemas)
    """
    # validate
    try:
        skill: Skill = Skill.objects.get(id=skill_id)
    except ObjectDoesNotExist:
        raise ValueError(f"The skill with id {skill_id} does not exist!")
    if skill not in skills.accumulate(
            personal=unit.template.unit,
            unit_class=unit.template.unit_class,
            extra=[*unit.template.extra_skills.all(), *unit.temp_skills.all()]
    ):
        raise ValueError(f"The skill {skill.name} is not one of the unit {unit.template.nickname}'s personal, "
                         f"class, or extra skills")
    if not skill.on_use_effect:
        raise ValueError(f"The skill {skill.name} cannot be used manually")
    # use skill (rely on skill implementation to return the proper output)
    # "activate_skill" should be purely cosmetic
    skill_output = [{
        "action": "activate_skill",
        "name": skill.name,
        "show": True
    }]
    if target_id is not None:
        try:
            target = ActiveUnit.objects.get(id=target_id)
        except ObjectDoesNotExist:
            raise ValueError(f"The skill {skill.name}'s target unit {target_id} does not exist")
        # validate using team_containing_unit()
        arena.team_containing_unit(target)
    else:
        target = None
    skill_output += skills.use[skill.on_use_effect](arena, unit, target, extra_data)
    arena.turn_should_end = True
    return skill_output


def discard_weapon(game: FireEmblemGame, unit: ActiveUnit, weapon_id: Union[int, ActiveWeapon]) -> List[Dict]:
    """
    Removes the weapon with the given ID from the unit's inventory, and if the weapon was
    previously equipped, equips the first eligible weapon in the unit's inventory.
    :param game: the game to use for Weapon Equipping Eligibility mechanics, for auto-equip
    :param unit: Unit holding the weapon to be discarded
    :param weapon_id: the ID of the weapon to be discarded, or for convenience, the weapon itself
    :return: a summary of this action, conforming to the format defined in the action_output_schema
    """
    # validate
    if not isinstance(weapon_id, ActiveWeapon):
        try:
            weapon: ActiveWeapon = ActiveWeapon.objects.get(id=weapon_id)
        except ObjectDoesNotExist:
            raise ValueError(f"The weapon with id {weapon_id} does not exist!")
    else:
        weapon = weapon_id
        weapon_id = weapon.id
    if weapon not in unit.weapons.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding weapon with id {weapon_id}")
    # execute
    output = remove_weapon_from_inventory(weapon, unit)
    # replace equipped weapon
    if weapon.equipped:
        possible_weapons = sorted(unit.weapons.all(), key=lambda w: w.inventory_id)
        for possible_weapon in possible_weapons:
            if ranks.unit_can_equip_weapon(game, unit, possible_weapon):
                output += equip_weapon(game, unit, possible_weapon)
                break
    # delete weapon
    logging.debug(f"Deleting ActiveWeapon {weapon_id} from database")
    weapon.delete()
    return output


def discard_item(unit: ActiveUnit, item_id: Union[int, ActiveItem]) -> List[Dict]:
    """
    Removes the item with the given ID from the unit's inventory. Does not automatically equip
    a new item.
    :param unit: Unit holding the weapon to be discarded
    :param item_id: the ID of the item to be discarded, or, for convenience, the item itself
    :return: a summary of this action, conforming to the format defined in the action_output_schema
    """
    # validate
    if not isinstance(item_id, ActiveItem):
        try:
            item: ActiveItem = ActiveItem.objects.get(id=item_id)
        except ObjectDoesNotExist:
            raise ValueError(f"The item with id {item_id} does not exist!")
    else:
        item = item_id
        item_id = item.id
    if item not in unit.items.all():
        raise ValueError(f"The active unit {unit.template.nickname} is not holding weapon with id {item_id}")
    # execute
    output = remove_item_from_inventory(item, unit)
    # delete item
    logging.debug(f"Deleting ActiveItem {item_id} from database")
    item.delete()
    return output


def attack(arena: ActiveArena, attacker: ActiveUnit, target: int, with_weapon: int, at_range: int) -> List[Dict]:
    """
    Calculates a round of combat between the given unit and the target. The unit will
    equip the given weapon and use it for the combat, while the target will use the first
    currently-equipped weapon found, or no weapon if none are equipped.
    If the defender does not exist, the attacker and defender are on the same team, or
    the unit's weapon cannot be attacked with, raises a ValueError.
    :param arena: the ActiveArena the battle is taking place in
    :param attacker: the attacking unit
    :param target: the ID of the defending unit
    :param with_weapon: the ID of the attacking unit's weapon
    :param at_range: the range at which the unit is attacking their target
    :return: a summary of the combat, conforming to the format defined in the action_output_schema
        (see api.arena.schemas)
    """
    # validate defender
    try:
        defender: ActiveUnit = ActiveUnit.objects.get(id=target)
    except ObjectDoesNotExist:
        raise ValueError("The intended target for this attack does not exist")
    attacker_team = arena.current_team()
    if attacker not in attacker_team.units.all():  # sanity check
        raise ValueError("The attacking unit is not on the team whose turn it is")
    if defender in attacker_team.units.all():
        raise ValueError("The attacker cannot attack their teammate")
    # load weapon
    output = equip_weapon(arena.game, attacker, with_weapon)
    weapon = ActiveWeapon.objects.get(id=with_weapon)
    print(weapon.to_dict())
    if weapon.uses == 0:
        raise ValueError(f"The weapon with id {with_weapon} has 0 uses remaining, and cannot be attacked with")
    if not (weapon.template.min_range <= at_range <= weapon.template.max_range):
        raise ValueError(f"Cannot attack at range {at_range} using weapon {weapon.name} with "
                         f"range {weapon.min_range}-{weapon.max_range}")
    # TODO reevaluate this maybe
    if weapon.template.min_range > 2:
        raise ValueError(f"Cannot use the weapon {weapon.name} in the Link Arena")
    # execute pre-combat actions
    combat_info: combat_data.CombatData = combat_data.CombatData(attacker, defender, arena, at_range)
    output += skills.before_combat_with_priority(
        skills1=skills.accumulate(
            personal=attacker.template.unit,
            unit_class=attacker.template.unit_class,
            active_weapons=[combat_info.attacker_weapon] if combat_info.attacker_weapon else [],
            active_items=defender.items.all(),
            extra=[*attacker.template.extra_skills.all(), *attacker.temp_skills.all()]
        ),
        unit1=attacker,
        skills2=skills.accumulate(
            personal=defender.template.unit,
            unit_class=defender.template.unit_class,
            active_weapons=[combat_info.defender_weapon] if combat_info.defender_weapon else [],
            active_items=defender.items.all(),
            extra=[*defender.template.extra_skills.all(), *defender.temp_skills.all()]
        ),
        unit2=defender,
        arena=arena,
        data=combat_info
    )
    # execute combat itself
    output.append(combat_info.generate_summary())
    output += combat.apply_skills_before_attacks(combat_info)
    output += combat.execute(arena, combat_info)
    # execute post-combat actions
    output += skills.after_combat_with_priority(
        skills1=skills.accumulate(
            personal=attacker.template.unit,
            unit_class=attacker.template.unit_class,
            active_weapons=[combat_info.attacker_weapon] if combat_info.attacker_weapon else [],
            active_items=attacker.items.all(),
            extra=[*attacker.template.extra_skills.all(), *attacker.temp_skills.all()]
        ),
        unit1=attacker,
        skills2=skills.accumulate(
            personal=defender.template.unit,
            unit_class=defender.template.unit_class,
            active_weapons=[combat_info.defender_weapon] if combat_info.defender_weapon else [],
            active_items=defender.items.all(),
            extra=[*defender.template.extra_skills.all(), *defender.temp_skills.all()]
        ),
        unit2=defender,
        arena=arena,
        data=combat_info
    )
    # evaluate outcome - broken weapons & dead units
    # no need to manually delete supports; cascading deletion should take care of that
    if attacker.current_hp <= 0:
        attacker_team.units.remove(attacker)
        output.append({
            "action": "kill_unit",
            "team": attacker_team.id,
            "unit": attacker.id
        })
        # since the attacker is the unit, we'll maybe delete them later on
    elif combat_info.attacker_weapon and combat_info.attacker_weapon.uses == 0:
        discard_weapon(arena.game, attacker, combat_info.attacker_weapon)
    defender_team = arena.team_containing_unit(defender)
    if defender.current_hp <= 0:
        defender_team.units.remove(defender)
        output.append({
            "action": "kill_unit",
            "team": defender_team.id,
            "unit": defender.id
        })
        logging.debug(f"Deleting ActiveUnit {defender.id} from database")
        defender.delete()
    elif combat_info.defender_weapon and combat_info.defender_weapon.uses == 0:
        discard_weapon(arena.game, defender, combat_info.defender_weapon)
    # conclude combat
    output.append({
        "action": "end_combat",
        "attacking_team": attacker_team.id,
        "points_to_attacker": combat_info.attacker_points,
        "defending_team": defender_team.id,
        "points_to_defender": combat_info.defender_points,
    })
    attacker_team.score += combat_info.attacker_points
    defender_team.score += combat_info.defender_points
    attacker.save()
    defender_team.save()
    arena.turn_should_end = True
    return output
