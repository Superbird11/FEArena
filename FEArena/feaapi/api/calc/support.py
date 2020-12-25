"""
file: calc/support.py

Helper methods for calculating boosts obtained from supports
"""
from typing import Dict, Optional, Iterable, Set
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveTeam import ActiveTeam
from ...models.build.RankedSupport import RankedSupport
from ...models.core.Unit import Unit, Affinity
from ...models.core.Game import BondSupportBehavior, RankedSupportBehavior


gba_affinity_boosts: Dict[Optional[str], Dict] = {
    Affinity.FIRE:    {"atk": 0.5, "prt": 0.0, "hit": 2.5, "avo": 2.5, "crit": 2.5, "ddg": 0.0},
    Affinity.THUNDER: {"atk": 0.0, "prt": 0.5, "hit": 0.0, "avo": 2.5, "crit": 2.5, "ddg": 2.5},
    Affinity.WIND:    {"atk": 0.5, "prt": 0.0, "hit": 2.5, "avo": 0.0, "crit": 2.5, "ddg": 2.5},
    Affinity.ICE:     {"atk": 0.0, "prt": 0.5, "hit": 2.5, "avo": 2.5, "crit": 0.0, "ddg": 2.5},
    Affinity.DARK:    {"atk": 0.0, "prt": 0.0, "hit": 2.5, "avo": 2.5, "crit": 2.5, "ddg": 2.5},
    Affinity.LIGHT:   {"atk": 0.5, "prt": 0.5, "hit": 2.5, "avo": 0.0, "crit": 2.5, "ddg": 0.0},
    Affinity.ANIMA:   {"atk": 0.5, "prt": 0.5, "hit": 0.0, "avo": 2.5, "crit": 0.0, "ddg": 2.5},
    None:             {"atk": 0.0, "prt": 0.0, "hit": 0.0, "avo": 0.0, "crit": 0.0, "ddg": 0.0},  # failsafe
}


def _gba_support_boost_for_unit(unit: ActiveUnit, team: ActiveTeam, stat: str) -> int:
    """
    Helper method that grabs the desired keys from the gba_affinity_boosts dict and adds them up
    """
    teammates: Set[Unit] = {bu.template.unit for bu in team.units.all()}
    ranked_supports: Iterable[RankedSupport] = RankedSupport.objects.filter(unit=unit.template)
    return int(sum(
        (gba_affinity_boosts[unit.template.unit.affinity][stat]
         + gba_affinity_boosts[rs.supported_by.affinity][stat]) * rs.rank
        for rs in ranked_supports
        if rs.supported_by in teammates
    ))


def hit_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Hit bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        unit_team: ActiveTeam = arena.team_containing_unit(unit)
        if unit_team.template.tactician_rank and unit_team.template.tactician_affinity \
                and unit_team.template.tactician_affinity == unit.template.unit.affinity:
            tactician_bonus = unit_team.template.tactician_rank
        else:
            tactician_bonus = 0
        return _gba_support_boost_for_unit(unit, unit_team, 'hit') + tactician_bonus
    # TODO implement ranked support behavior for various games


def crit_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Crit bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        return _gba_support_boost_for_unit(unit, arena.team_containing_unit(unit), 'crit')
    # TODO implement ranked support behavior for various games


def avo_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Avo bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        unit_team: ActiveTeam = arena.team_containing_unit(unit)
        if unit_team.template.tactician_rank and unit_team.template.tactician_affinity \
                and unit_team.template.tactician_affinity == unit.template.unit.affinity:
            tactician_bonus = unit_team.template.tactician_rank
        else:
            tactician_bonus = 0
        return _gba_support_boost_for_unit(unit, unit_team, 'avo') + tactician_bonus
    # TODO implement ranked support behavior for various games


def ddg_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Ddg bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        unit_team: ActiveTeam = arena.team_containing_unit(unit)
        if unit_team.template.tactician_rank and unit_team.template.tactician_affinity \
                and unit_team.template.tactician_affinity == unit.template.unit.affinity:
            tactician_bonus = unit_team.template.tactician_rank
        else:
            tactician_bonus = 0
        return _gba_support_boost_for_unit(unit, unit_team, 'ddg') + tactician_bonus
    # TODO implement ranked support behavior for various games


def atk_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Atk bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        return _gba_support_boost_for_unit(unit, arena.team_containing_unit(unit), 'atk')
    # TODO implement ranked support behavior for various games


def prt_rsl_boosts(arena: ActiveArena, unit: ActiveUnit) -> int:
    """
    :param arena: the arena in which the current combat is taking place
    :param unit: unit to check support bonuses for
    :return: the total Prt or Rsl bonus for this unit provided by their bond and ranked supports
    """
    game = arena.game
    # bond supports
    bond_support_method = game.bond_support_behavior
    if bond_support_method != BondSupportBehavior.NONE:
        # TODO implement bond supports for various games
        pass
    # ranked supports
    ranked_support_method = game.ranked_support_behavior
    if ranked_support_method == RankedSupportBehavior.GBA_AFFINITY:
        return _gba_support_boost_for_unit(unit, arena.team_containing_unit(unit), 'prt')
    # TODO implement ranked support behavior for various games
