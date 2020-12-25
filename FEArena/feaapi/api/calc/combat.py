from typing import List, Dict
from math import sin, radians
import random
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveArena import ActiveArena
from ...models.core.Game import FireEmblemGame
from ...models.core.Game import CritDamageCalculationMethod
from ...models.core.Game import HitRNGMethod
from ...models.core.Game import EXPFormula
from .combat_data import AfterAttackData, CombatData
from . import stats
from .. import skills


def apply_skills_before_attacks(data: CombatData) -> List[Dict]:
    """
    Goes through each of the attacks in the combat data, and for each of them,
    applies the attacker's before_attack and the defender's before_attacked.
    :param data: the combat data to sort through
    :return: a summary of skill activations, if applicable, conforming to the
        action_output_schema.
    """
    output = []
    for attack in data.attack_data:
        output += skills.before_attack_with_priority(
            attacker=skills.accumulate(
                personal=attack.by.template.unit,
                unit_class=attack.by.template.unit_class,
                active_weapons=[attack.with_weapon],
                active_items=attack.by.items.all(),
                extra=[*attack.by.template.extra_skills.all(), *attack.by.temp_skills.all()],
            ),
            attacked=skills.accumulate(
                personal=attack.against.template.unit,
                unit_class=attack.against.template.unit_class,
                active_weapons=[attack.with_weapon],
                active_items=attack.against.items.all(),
                extra=[*attack.against.template.extra_skills.all(), *attack.against.temp_skills.all()],
            ),
            data=attack
        )
    return output


def execute(arena: ActiveArena, data: CombatData) -> List[Dict]:
    """
    Plays out the round of combat contained in the given CombatData,
    making the appropriate changes to the attacker and defender, and
    producing a summary.
    :param arena: the ActiveArena in which combat is happening
    :param data: combat data to play out
    :return: a summary of the combat, conforming to the action_output_schema
        (see api.arena.schemas)
    """
    output = []
    attacker_initial_hp = data.attacker.current_hp
    defender_initial_hp = data.defender.current_hp
    for attack in data.attack_data:
        # if weapon has zero durability, or if either combatant has less than zero HP,
        # don't follow through with this attack, and remove it from the attack data
        if attack.with_weapon.uses == 0 or attack.by.current_hp <= 0 or attack.against.current_hp <= 0:
            data.remove_attack(attack)
            continue
        # roll hit
        hit_chance = attack.hit - attack.avo
        if data.game.rng_method == HitRNGMethod.ONE_RN:
            attack_hit = random.randint(0, 99) < hit_chance
        elif data.game.rng_method == HitRNGMethod.TWO_RN:
            avg_roll = (random.randint(0, 99) + random.randint(0, 99)) // 2
            attack_hit = avg_roll < hit_chance
        elif data.game.rng_method == HitRNGMethod.HYBRID:
            # True hit rate: (Hit rate × 100) + ((40 / 3) × Hit rate × sin((0.02(Hit rate) - 1) × 180)
            true_hit = (hit_chance * 100) + \
                       ((40 / 3) * hit_chance * sin(radians((0.02 * hit_chance - 1) * 180))) * (hit_chance >= 50)
            attack_hit = random.randint(0, 9999) < true_hit
        else:
            raise ValueError(f"Unrecognized Hit RNG method '{data.game.rng_method}' for game {data.game.name}")
        if not attack_hit:
            attack_result = AfterAttackData(
                by=attack.by,
                weapon=attack.with_weapon,
                against=attack.against,
                miss=True,
                tags=attack.tags,
                crit=False,
                dmg=0,
            )
        else:
            # roll crit
            crit_chance = attack.crit - attack.ddg
            attack_crit = random.randint(0, 99) < crit_chance
            # calculate damage
            if attack_crit:
                if data.game.crit_damage == CritDamageCalculationMethod.ATK_TIMES_2:
                    dmg = attack.atk * 2 - attack.prt_rsl
                elif data.game.crit_damage == CritDamageCalculationMethod.DMG_TIMES_3:
                    dmg = (attack.atk - attack.prt_rsl) * 3
                else:
                    raise ValueError(f"Unrecognized Crit Damage method '{data.game.crit_damage}' "
                                     f"for game {data.game.name}")
            else:
                dmg = attack.atk - attack.prt_rsl
            dmg = max(dmg, data.game.min_damage_per_attack)
            attack_result = AfterAttackData(
                by=attack.by,
                weapon=attack.with_weapon,
                against=attack.against,
                miss=False,
                tags=attack.tags,
                crit=attack_crit,
                dmg=dmg,
            )
            # deduct health
            attack.against.current_hp -= dmg
            # deduct weapon durability
            attack.with_weapon.uses -= 1
        # now that the core of the attack has been executed, activate after-attack skills
        output.append(attack_result.to_dict())
        output += skills.after_attack_all(
            sorted(
                skills.accumulate(
                    personal=attack.by.template.unit,
                    unit_class=attack.by.template.unit_class,
                    active_weapons=[attack.with_weapon],
                    active_items=attack.by.items.all(),
                    extra=[*attack.by.template.extra_skills.all(), *attack.by.temp_skills.all()]
                ), key=lambda skl: -skl.priority
            ), arena, attack_result
        )
        output += skills.after_attacked_all(
            sorted(
                skills.accumulate(
                    personal=attack.against.template.unit,
                    unit_class=attack.against.template.unit_class,
                    active_weapons=[attack.against_weapon],
                    active_items=attack.against.items.all(),
                    extra=[*attack.against.template.extra_skills.all(), *attack.against.temp_skills.all()]
                ), key=lambda skl: -skl.priority
            ), attack_result
        )
        # and finally, continue to the next attack.
    # when all attacks in the combat have been done, calculate EXP for both sides:
    data.attacker_points += calculate_exp(data.game, data.attacker, data.defender,
                                          defender_initial_hp - data.defender.current_hp)
    data.defender_points += calculate_exp(data.game, data.defender, data.attacker,
                                          attacker_initial_hp - data.attacker.current_hp)
    data.attacker_weapon.save()
    data.attacker.save()
    if data.defender_weapon:
        data.defender_weapon.save()
    data.defender.save()
    return output


def calculate_exp(game: FireEmblemGame, unit: ActiveUnit, enemy: ActiveUnit, dmg_dealt: int) -> int:
    """
    Using a game-specific EXP formula, calculates the amount of EXP a combat would result
    in for units on either side, intended to be used for calculating points earned from
    a combat.
    :param game: game whose mechanics to use for EXP calculation
    :param unit: unit making the attack
    :param enemy: unit being attacked
    :param dmg_dealt: total damage dealt by for_unit to against_unit during combat
    :return: the amount of EXP for_unit should earn from this combat
    """
    method = game.exp_method
    if method == EXPFormula.FE1:
        if dmg_dealt == 0:
            return 0
        if enemy.current_hp > 0:
            return min(dmg_dealt, 20)
        return enemy.template.unit_class.class_exp + enemy.template.unit_level - 1
    elif method == EXPFormula.FE3:
        if dmg_dealt == 0:
            return 0
        if enemy.current_hp > 0:
            return min(dmg_dealt, 10)
        return enemy.template.unit_class.class_exp
    elif method == EXPFormula.FE2:
        if dmg_dealt == 0 and unit.current_hp <= 0:
            return 0
        if dmg_dealt == 0:
            return 1
        if unit.template.unit_level <= 2:
            level_factor = 10
        elif unit.template.unit_level >= 10:
            level_factor = 2
        else:
            level_factor = 12 - unit.template.unit_level
        kill_exp = max(min(enemy.template.unit_class.class_exp * (enemy.template.unit_level + 9) / 10, 255)
                       * unit.template.unit_class.class_strength * level_factor / 100, 1)
        if enemy.current_hp > 0:
            return int(kill_exp * dmg_dealt / (2 * stats.calc_max_hp(enemy)))
        else:
            return int(kill_exp)
    elif method == EXPFormula.FE4:
        if dmg_dealt == 0:
            return 0
        elif enemy.current_hp > 0:
            return max(10 + (enemy.template.unit_level - unit.template.unit_level), 0)
        return max(30 + (enemy.template.unit_level - unit.template.unit_level) * 2, 0)
    elif method == EXPFormula.FE5:
        if dmg_dealt == 0:
            return 0
        damage_exp = int((31 - unit.template.unit_level) - unit.template.unit_class.class_strength)
        if enemy.current_hp > 0:
            return damage_exp
        return max((enemy.template.unit_class.class_strength *
                    (enemy.template.unit_level + 20 * enemy.template.unit_class.promoted))
                   - (unit.template.unit_class.class_strength
                      * (unit.template.unit_level + 20 * unit.template.unit_class.promoted)) + 20, 0) + damage_exp
    elif method in (EXPFormula.GBA_EASY, EXPFormula.GBA_HARD):
        if dmg_dealt == 0 and unit.current_hp <= 0:
            return 0
        if dmg_dealt == 0:
            return 1
        damage_exp = max(
            int(
                (
                    31 + enemy.template.unit_level + 20 * enemy.template.unit_class.promoted
                    - unit.template.unit_level - 20 * unit.template.unit_class.promoted
                ) / unit.template.unit_class.class_strength
            ), 1
        )
        if enemy.current_hp > 0:
            return min(damage_exp, 100)
        else:
            enemy_bonus = enemy.template.unit_level * enemy.template.unit_class.class_strength + \
                enemy.template.unit_class.class_exp
            unit_bonus = unit.template.unit_level * unit.template.unit_class.class_strength + \
                unit.template.unit_class.class_exp
            # NOTE: I'm tentatively making this check >= instead of >, because research on this is hard to
            # come by and I'm not in much of a position to experiment. And I kind of want to be generous
            if method == EXPFormula.GBA_EASY and unit_bonus >= enemy_bonus:
                mode_divisor = 2
            else:
                mode_divisor = 1
            return min(max(damage_exp + enemy_bonus - unit_bonus // mode_divisor + 20, damage_exp), 100)
    elif method in (EXPFormula.FE9, EXPFormula.FE9_EASY, EXPFormula.FE9_HARD, EXPFormula.FE9_MANIAC):
        if dmg_dealt == 0 and unit.current_hp <= 0:
            return 0
        if dmg_dealt == 0:
            return 1
        unit_power = unit.template.unit_level + 20 * unit.template.unit_class.promoted
        enemy_power = enemy.template.unit_level + 20 * enemy.template.unit_class.promoted
        battle_exp_base = (21 + (enemy_power - unit_power)) // 2 + 5 * (method == EXPFormula.FE9_EASY)
        if enemy.current_hp > 0:
            return battle_exp_base
        else:
            if method == EXPFormula.FE9_EASY:
                mode_bonus = 30
            elif method == EXPFormula.FE9_HARD:
                mode_bonus = 15
            elif method == EXPFormula.FE9_MANIAC:
                mode_bonus = 10
            else:
                mode_bonus = 20
            return battle_exp_base + (enemy_power - unit_power) + mode_bonus
    elif method in (EXPFormula.FE10, EXPFormula.FE10_HARD):
        # This formula is not datamined, is experimental. Reference:
        # https://gamefaqs.gamespot.com/boards/932999-fire-emblem-radiant-dawn/48343453
        if dmg_dealt == 0 and unit.current_hp <= 0:
            return 0
        if dmg_dealt == 0:
            return 1
        unit_level = unit.template.unit_level * unit.template.unit_class.class_exp \
            + 20 * unit.template.unit_class.promoted + 20 \
            * (unit.template.unit_class.promoted and unit.template.unit_class.promotes_to.all().count == 0)
        enemy_level = enemy.template.unit_level * enemy.template.unit_class.class_exp \
            + 20 * enemy.template.unit_class.promoted + 20 \
            * (enemy.template.unit_class.promoted and enemy.template.unit_class.promotes_to.all().count == 0)
        attack_exp = 10 + (enemy_level - unit_level) // 2 - 5 * (method == EXPFormula.FE10_HARD)
        if enemy.current_hp > 0:
            return attack_exp
        else:
            return attack_exp + (enemy_level - unit_level) + \
                   (enemy.template.unit_class.class_strength - unit.template.unit_class.class_strength) + 15
    elif method == EXPFormula.FE11:
        # source: Serenes Forest (probably slightly wrong)
        if dmg_dealt == 0:
            return 0
        level_diff = enemy.template.unit_level + 15 * enemy.template.unit_class.promoted \
            - unit.template.unit_level + 15 * unit.template.unit_class.promoted
        if enemy.current_hp > 0:
            if 0 >= level_diff >= -2:
                return 10
            if level_diff > 0:
                return (31 + level_diff) // 3
            return (33 + level_diff) // 3
        else:
            if 0 >= level_diff >= -2:
                kill_exp = 30
            elif level_diff > 0:
                kill_exp = 30 + level_diff * 3.33
            else:
                kill_exp = 37 + level_diff * 3.33
            kill_exp += enemy.template.unit_class.class_exp
            if kill_exp < 15:
                return max(int((54 + level_diff) / 3), 8)
            return int(kill_exp)
    elif method == EXPFormula.FE12:
        # source: Serenes Forest (probably slightly wrong)
        if dmg_dealt == 0:
            return 0
        level_diff = enemy.template.unit_level + 15 * enemy.template.unit_class.promoted \
            - unit.template.unit_level + 15 * unit.template.unit_class.promoted
        if enemy.current_hp > 0:
            if level_diff >= 0:
                return (31 + level_diff) // unit.template.unit_class.class_strength
            else:
                return (33 + level_diff) // unit.template.unit_class.class_strength
        else:
            if unit.template.unit_class.class_strength == 5:
                level_diff_factor = 31/6
                fallover_base_exp = 68
                if enemy.template.unit_class.class_strength == 5:
                    enemy_level_factor = 0
                    base_exp_eq = 46
                    base_exp_gt = 46
                    base_exp_lt = 56
                else:
                    enemy_level_factor = -2
                    base_exp_eq = 24
                    base_exp_gt = 26
                    base_exp_lt = 32
            else:
                level_diff_factor = 10/3
                fallover_base_exp = 54
                if enemy.template.unit_class.class_strength == 5:
                    enemy_level_factor = 2
                    base_exp_eq = 52
                    base_exp_gt = 50
                    base_exp_lt = 61
                else:
                    enemy_level_factor = 0
                    base_exp_eq = 30
                    base_exp_gt = 30
                    base_exp_lt = 37
        if level_diff == 0:
            kill_exp = int(base_exp_eq + enemy_level_factor * enemy.template.unit_level
                           + enemy.template.unit_class.class_exp)
        elif level_diff > 0:
            kill_exp = int(base_exp_gt + level_diff * level_diff_factor + enemy_level_factor * enemy.template.unit_level
                           + enemy.template.unit_class.class_exp)
        else:
            kill_exp = int(base_exp_lt + level_diff * level_diff_factor + enemy_level_factor * enemy.template.unit_level
                           + enemy.template.unit_class.class_exp)
        if kill_exp < 15:
            return (fallover_base_exp + level_diff) // unit.template.unit_class.class_strength
        else:
            return kill_exp
    elif method == EXPFormula.FE13:
        # extrapolated from https://forums.serenesforest.net/index.php?/topic/43176-awakening-exp-formula/
        # Ignoring Lunatic repeated-attack penalty, and also ignoring internal level entirely
        # also ignoring individual unit EXP bonuses, as those are essentially boss bonuses
        if dmg_dealt == 0 and unit.current_hp <= 0:
            return 0
        if dmg_dealt == 0:
            return 1
        level_difference = (enemy.template.unit_level + 20 * enemy.template.unit_class.promoted) \
            - (unit.template.unit_level + 20 * unit.template.unit_class.promoted)
        if level_difference >= 0:
            hit_exp = (31 + level_difference) // 3
            kill_exp = 20 + level_difference * 3 + enemy.template.unit_class.class_exp
        elif level_difference == -1:
            hit_exp = 10
            kill_exp = 20 + enemy.template.unit_class.class_exp
        else:
            hit_exp = max((33 + level_difference) / 3, 1)
            kill_exp = max(26 + level_difference * 3 + enemy.template.unit_class.class_exp, 7)
        if enemy.current_hp > 0:
            return hit_exp
        else:
            return hit_exp + kill_exp
    elif method in [EXPFormula.FE16, EXPFormula.FE16_HARD, EXPFormula.FE16_MADDENING]:
        # https://forums.serenesforest.net/index.php?/topic/89413-healingsupport-action-exp-formula-exp-table-from-level-1-to-50/
        # Basic transcription of the calculation:
        # <Basic points when killing an enemy>
        # 	[A] Base experience value = (1) * (2) / 100
        # 	[B] Book experience = [A] * (3) / 100
        # 	[C] Time Basic Experience Value = [B] * (4) / 100
        # 		(1) Enemy unit class base EXP (as shown on page 536, presumably)
        # 		(2) Number level correction Percentage = 20 * (100 + Unit Level - 1)
        # 		(3) Level difference correction: with key enemy level - unit level -> (see table below)
        # 		(4) Enemy General Correction: if enemy is a monster or boss = 2, otherwise 1 (we ignore this)
        #
        # <Basic experience points when hitting an enemy but not killing>
        # 	Experience value = [C] * {damage inflicted} / {max HP of enemy unit} / 2
        if dmg_dealt == 0:
            return 0
        base_exp_value = enemy.template.unit_class.class_exp * 20 * (99 + unit.template.unit_level) / 100
        level_diff = max(min(enemy.template.unit_level - unit.template.unit_level, -20), 20)
        difficulty_idx = [str(EXPFormula.FE16), EXPFormula.FE16_HARD, EXPFormula.FE16_MADDENING].index(method)
        kill_exp = base_exp_value * fe16_level_difference_table[level_diff][difficulty_idx]
        if enemy.current_hp <= 0:
            return int(kill_exp)
        return int(kill_exp * dmg_dealt / (2 * stats.calc_max_hp(enemy)))
    else:
        raise ValueError(f"Unrecognized EXP calculation method {method} for game {game.name}")


fe16_level_difference_table = {
    20: [250, 150, 60],
    19: [230, 140, 55],
    18: [220, 130, 55],
    17: [210, 120, 55],
    16: [200, 115, 55],
    15: [195, 115, 55],
    14: [190, 110, 50],
    13: [185, 110, 50],
    12: [180, 110, 50],
    11: [175, 110, 50],
    10: [170, 110, 50],
    9: [165, 105, 45],
    8: [160, 105, 45],
    7: [155, 100, 45],
    6: [150, 100, 45],
    5: [125, 100, 45],
    4: [120, 95, 45],
    3: [115, 90, 40],
    2: [110, 85, 40],
    1: [110, 80, 30],
    0: [105, 70, 20],
    -1: [100, 60, 15],
    -2: [95, 50, 10],
    -3: [90, 40, 5],
    -4: [85, 30, 1],
    -5: [80, 20, 1],
    -6: [75, 10, 1],
    -7: [70, 5, 1],
    -8: [65, 5, 1],
    -9: [60, 5, 1],
    -10: [55, 5, 1],
    -11: [50, 5, 1],
    -12: [40, 5, 1],
    -13: [30, 5, 1],
    -14: [20, 5, 1],
    -15: [10, 5, 1],
    -16: [10, 5, 1],
    -17: [10, 5, 1],
    -18: [10, 5, 1],
    -19: [10, 5, 1],
    -20: [0, 0, 0],
}
