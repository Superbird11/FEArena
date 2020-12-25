from typing import Dict, Callable, Union, Optional, Any
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveItem import ActiveItem
from ..calc import stats
from ..arena.helper import remove_item_from_inventory


def _(_: ActiveArena, __: ActiveUnit) -> None:
    pass


def dance_single(arena: ActiveArena, unit: ActiveUnit, target: ActiveUnit, _: Any) -> None:
    """
    Restores another unit, giving them the ability to move again. Raises a ValueError
    if the unit in question has not already moved.
    Has no effect in regular Link Battles, only in skirmishes, which are not yet implemented.
    """
    # TODO implement Dance when implementing skirmishes
    return None


def fe7_steal(arena: ActiveArena, unit: ActiveUnit, target: ActiveUnit, item: str) -> Dict:
    """
    Tries to steal the given item from the target. Raises a ValueError if the unit's
    Spd isn't high enough, if the target isn't holding the item, if the item is a
    weapon/staff, or if the unit's inventory is full
    """
    if target is None:
        raise ValueError("Steal skill requires a target")
    if item is None:
        raise ValueError("Steal skill requires an item ID belonging to target")
    if stats.calc_spd(unit) < stats.calc_spd(target):
        raise ValueError("Unit's Spd is not high enough to steal from target unit")
    try:
        item_id = int(item)
    except ValueError:
        raise ValueError("The extra_data provided was not an integer")
    if target.items.filter(id=item_id).count() == 0:
        raise ValueError("Target is not holding item")
    if unit.items.count() + 1 >= arena.game.max_inventory_items:
        raise ValueError("Unit is holding too many items and cannot steal")
    new_inventory_id = max(max(w.id for w in unit.weapons.all()), max(i.id for i in unit.items.all()))
    if new_inventory_id >= arena.game.max_inventory_size:
        raise ValueError("Unit's inventory is full, so unit cannot steal")
    target_item: ActiveItem = target.items.get(id=item_id)
    remove_item_from_inventory(target_item, target)
    target_item.inventory_id = new_inventory_id
    unit.items.add(target_item)
    return {
        "action": "steal_item",
        "unit": unit.id,
        "from": target.id,
        "item": target_item.id
    }


use: Dict[Union[str, None], Callable[[ActiveArena, ActiveUnit, Optional[ActiveUnit], Optional[str]],
                                     Union[Dict, None]]] = {
    "dance_single": dance_single,
    "fe7_steal": fe7_steal,
    None: _
}
