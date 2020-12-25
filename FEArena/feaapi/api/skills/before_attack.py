from typing import Dict, Callable, Union
import random
from ..calc.combat_data import AttackData
from ..calc import stats


def _(_: AttackData) -> None:
    pass


def fe7_silencer(atk: AttackData) -> None:
    """
    With a crit/2% chance to activate, deals damage equal to the opponent's remaining HP.
    Prevents other skills from activating on this attack.

    Actually simply runs the hit calculation using 2RN, runs the crit calculation, and if Silencer
    would activate, sets them both to 100%
    """
    if atk.skillable:
        avg_roll = (random.randint(0, 99) + random.randint(0, 99)) // 2
        if avg_roll < atk.hit - atk.avo and random.randint(0, 99) < (atk.crit - atk.ddg) / 2:
            # silencer activates
            atk.dmg = atk.against.current_hp
            atk.hit = 999
            atk.crit = 999
            atk.tags.append("silencer")
            atk.skillable = False
    return None


def fe7_devil(atk: AttackData) -> None:
    """
    Rolls a random number [0-99], and if the number is less than (31 - Unit's Luck),
    then sets the attacker as the defender for their own attack. Does not change any
    other numbers (Hit, Crit, Prt, etc.) remain the same).
    Also, does not return any particular message.
    """
    luk = stats.calc_luk(atk.by)
    if random.randint(0, 99) < (31 - luk):
        atk.against = atk.by
    return None


def brave(atk: AttackData) -> None:
    """
    Adds another attack after this one, identical to it.
    """
    if "brave" not in atk.tags:
        atk.append(AttackData(
            by=atk.by,
            against=atk.against,
            with_weapon=atk.with_weapon,
            against_weapon=atk.against_weapon,
            atk=atk.atk,
            prt_rsl=atk.prt_rsl,
            hit=atk.hit,
            avo=atk.avo,
            crit=atk.crit,
            ddg=atk.ddg,
            skillable=atk.skillable,
            counterattack=atk.counterattack,
            followup=atk.followup,
            tags=["brave"] + atk.tags[:]
        ))


before_attack: Dict[Union[str, None], Callable[[AttackData], Union[Dict, None]]] = {
    'brave': brave,
    'fe7_devil': fe7_devil,
    'fe7_silencer': fe7_silencer,
    None: _,
}
