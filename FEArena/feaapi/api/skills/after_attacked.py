from typing import Dict, Callable, Union
from ..calc.combat_data import AfterAttackData


def _(_: AfterAttackData) -> None:
    pass


after_attacked: Dict[Union[str, None], Callable[[AfterAttackData], Union[Dict, None]]] = {
    None: _
}
