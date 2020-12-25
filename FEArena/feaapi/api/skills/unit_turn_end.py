from typing import Dict, Callable, Union, List
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit


def _(_: ActiveArena, __: ActiveUnit, _actions_taken: List[Dict]) -> None:
    pass


unit_turn_end: Dict[Union[str, None], Callable[[ActiveArena, ActiveUnit, List[Dict]], Union[Dict, None]]] = {
    None: _
}
