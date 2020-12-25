from typing import Dict, Callable, Union
from ..calc.combat_data import AttackData


def _(_: AttackData) -> None:
    pass


before_attacked: Dict[Union[str, None], Callable[[AttackData], Union[Dict, None]]] = {
    None: _
}
