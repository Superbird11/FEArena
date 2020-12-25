"""
file: arena/helper.py

Helper methods.
"""
import operator
import logging
from typing import Union, List, Dict
from threading import Timer
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.play.ActiveItem import ActiveItem
from ...models.play.ActiveUnit import ActiveUnit


def _move_inventory_in_direction(inventory_id: int, unit: ActiveUnit, direction: bool) -> List[Dict]:
    """
    :param inventory_id: where to start
    :param unit: unit to make change for
    :param direction: True -> move everything before inventory_id backwards;
                      False -> move everything after inventory_id forwards
    """
    op = operator.lt if direction else operator.gt
    change = 1 if direction else -1
    output = []
    for weapon in unit.weapons.all():
        if op(weapon.inventory_id, inventory_id):
            weapon.inventory_id += change
            output.append({
                "action": f"change_weapon_inventory_id",
                "unit": weapon.id,
                "weapon": weapon.id,
                "new_id": weapon.inventory_id,
            })
    for item in unit.items.all():
        if op(item.inventory_id, inventory_id):
            item.inventory_id += change
            output.append({
                "action": f"change_item_inventory_id",
                "unit": item.id,
                "item": item.id,
                "new_id": item.inventory_id,
            })
    return output


def _shift_thing_to_front_of_inventory(this: Union[ActiveWeapon, ActiveItem], unit: ActiveUnit, kw: str) -> List[Dict]:
    output = _move_inventory_in_direction(this.inventory_id, unit, True)
    this.inventory_id = 0
    output.append({
        "action": f"change_{kw}_inventory_id",
        "unit": unit.id,
        kw: this.id,
        "new_id": 0,
    })
    return output


def shift_item_to_front_of_inventory(this: ActiveItem, unit: ActiveUnit) -> List[Dict]:
    """
    Sets the given weapon/item's inventory_id to 0, and shifts back every other item in
    the unit's inventory (weapons and items) by one until there's space for everything.
    Returns a list of inventory_id change messages.
    This method DOES NOT VALIDATE that the item in question actually belongs to this unit.
    :param this: an ActiveItem to move to the front of the inventory
    :param unit: a unit in whose inventory to move the given item
    :return: a list of inventory_id change messages, conforming to the action_output_schema
        (see api/arenas/schemas.py)
    """
    return _shift_thing_to_front_of_inventory(this, unit, 'item')


def shift_weapon_to_front_of_inventory(this: ActiveWeapon, unit: ActiveUnit) -> List[Dict]:
    """
    Sets the given weapon's inventory_id to 0, and shifts back every other item in the
    unit's inventory (weapons and items) by one until there's space for everything.
    Returns a list of inventory_id change methods.
    This method DOES NOT VALIDATE the weapon in question actually belongs to this unit.
    :param this: an ActiveWeapon to move to the front of the inventory
    :param unit: a unit in whose inventory to move the given weapon
    :return: a list of inventory_id change messages, conforming to the action_output_schema
        (see api/arenas/schemas.py)
    """
    return _shift_thing_to_front_of_inventory(this, unit, 'weapon')


def remove_weapon_from_inventory(this: ActiveWeapon, unit: ActiveUnit) -> List[Dict]:
    """
    Removes the given weapon from the unit's inventory, and shifts every item in the inventory
    after it forwards.
    This method DOES NOT VALIDATE that the weapon in question actually belongs to this unit.
    :param this: ActiveWeapon to remove from inventory
    :param unit: unit from whose inventory to remove weapon
    :return: a list of inventory_id change messages and a weapon_removal message, conforming
        action_output_schema (see api/arenas/schemas.py)
    """
    output = _move_inventory_in_direction(this.inventory_id, unit, False)
    unit.weapons.remove(this)
    output.append({
        "action": "remove_weapon",
        "weapon": this.id,
        "unit": unit.id,
    })
    return output


def remove_item_from_inventory(this: ActiveItem, unit: ActiveUnit) -> List[Dict]:
    """
    Removes the given item from the unit's inventory, and shifts every item in the inventory
    after it forwards.
    This method DOES NOT VALIDATE that the weapon in question actually belongs to this unit.
    :param this: ActiveItem to remove from inventory
    :param unit: unit from whose inventory to remove weapon
    :return: a list of inventory_id change messages and an item_removal message, conforming
        action_output_schema (see api/arenas/schemas.py)
    """
    output = _move_inventory_in_direction(this.inventory_id, unit, False)
    unit.items.remove(this)
    output.append({
        "action": "remove_item",
        "item": this.id,
        "unit": unit.id,
    })
    return output


def save_arena(arena: ActiveArena):
    """
    Saves changes to the database for this ActiveArena and all related objects, from the bottom up
    :param arena: Arena to save
    """
    # foreign keys must be saved individually before their targets, so do that first.
    # note that Built objects (i.e. templates) and core objects (i.e. arena.game) should
    # not need to be saved, as they should not have changed
    logging.debug(f"Saving arena {arena.id} and all sub-objects to database")
    for team in arena.teams():
        for unit in team.units.all():
            for weapon in unit.weapons.all():
                weapon.save()
            for item in unit.items.all():
                item.save()
            unit.save()
        team.save()
    arena.save()


def tear_down_arena(arena: ActiveArena):
    """
    Deletes all Active components of this arena, then deletes this arena
    :param arena: Arena to delete
    """
    # prepare to do so
    def finish_tear_down_arena():
        # ignore Built and Core components
        logging.debug(f"Deleting arena {arena.id} and all sub-objects from database")
        for team in arena.teams():
            for unit in team.units.all():
                for weapon in unit.weapons.all():
                    weapon.delete()
                for item in unit.items.all():
                    item.delete()
                unit.delete()
            team.delete()
        arena.delete()
    # set a timer
    Timer(60 * 15, finish_tear_down_arena).start()


__all__ = [
    'shift_item_to_front_of_inventory',
    'shift_weapon_to_front_of_inventory',
    'remove_weapon_from_inventory',
    'remove_item_from_inventory',
    'save_arena',
    'tear_down_arena',
]

