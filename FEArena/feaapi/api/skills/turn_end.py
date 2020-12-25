from typing import Dict, Callable, Union
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit


def _(_: ActiveArena, __: ActiveUnit) -> None:
    pass


turn_end: Dict[Union[str, None], Callable[[ActiveArena, ActiveUnit], Union[Dict, None]]] = {
    None: _
}
