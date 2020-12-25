"""
file: combat_data.py

A separate file containing helper classes for skills to process on,
separated from its parent combat.py to avoid circular import issues
"""
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from typing import Union, List, Iterator, Dict
from ...models.core.Game import FollowUpCriteria
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play.ActiveWeapon import ActiveWeapon
from ...models.play.ActiveArena import ActiveArena
from . import battle_stats


class AttackData:
    """
    A class representing the data of a single attack.
    The chain of attacks belonging to a combat phase behaves like a linked list:
    each has a .next property that leads to the next attack in combat.
    This allows individual AttackData to add more attacks after themselves, as
    required by some skills. An AttackData is iterable, and will yield successive
    attacks.
    """

    def __init__(self, by: ActiveUnit, against: ActiveUnit, with_weapon: ActiveWeapon, against_weapon: ActiveWeapon,
                 atk: int, prt_rsl: int, hit: int, avo: int, crit: int, ddg: int,
                 skillable=True, counterattack: bool = False, followup: bool = False, tags: List[str] = None,
                 next_attack: Union['AttackData', None] = None):
        self.by = by
        self.against = against
        self.with_weapon = with_weapon
        self.against_weapon = against_weapon
        self.atk = atk
        self.prt_rsl = prt_rsl
        self.hit = hit
        self.avo = avo
        self.crit = crit
        self.ddg = ddg
        self.skillable = skillable
        self.counterattack = counterattack
        self.followup = followup
        # tags are both used by skill processing to avoid conflicts, and by the frontend skill
        # renderer to determine whether to show a particular animation
        self.tags = tags if tags else []
        self.next = next_attack

    def replace(self, other: 'AttackData'):
        """
        Replaces every property except 'next' of this AttackData with the corresponding
        property of the other AttackData
        :param other: AttackData to use as template
        """
        self.by = other.by
        self.against = other.against
        self.with_weapon = other.with_weapon
        self.against_weapon = other.against_weapon
        self.atk = other.atk
        self.prt_rsl = other.prt_rsl
        self.hit = other.hit
        self.avo = other.avo
        self.crit = other.crit
        self.ddg = other.ddg
        self.skillable = other.skillable
        self.counterattack = other.counterattack
        self.followup = other.followup
        self.tags = other.tags
        # do not replace next()

    def append(self, other: 'AttackData'):
        """
        Sets the given AttackData as the next attack, to come after this one.
        If this AttackData already had a .next, replaces the given
        AttackData's .next with this AttackData's .next
        :param other: AttackData to place immediately after this one
        :return: the AttackData that was added
        """
        if self.next:
            other.next = self.next
        self.next = other
        return self.next

    def __iter__(self) -> Iterator['AttackData']:
        cur = self
        while cur:
            yield cur
            cur = cur.next


class CombatData:
    def __init__(self, attacker: ActiveUnit, defender: ActiveUnit, arena: ActiveArena, at_range: int):
        self.arena = arena
        self.game = arena.game
        self.range = at_range
        # get attacker's weapon data
        self.attacker = attacker
        try:
            self.attacker_weapon: ActiveWeapon = attacker.weapons.get(equipped=True)
        except ObjectDoesNotExist:
            raise ValueError("Attacker cannot attack with no equipped weapon")
        except MultipleObjectsReturned:
            raise ValueError("Attacker has multiple equipped weapons")
        attacker_weapon_type = self.attacker_weapon.template.weapon_type if self.attacker_weapon else None
        # get defender's weapon data
        self.defender = defender
        try:
            self.defender_weapon: Union[ActiveWeapon, None] = defender.weapons.get(equipped=True)
        except ObjectDoesNotExist:
            self.defender_weapon: Union[ActiveWeapon, None] = None
        except MultipleObjectsReturned:
            raise ValueError("Defender has multiple equipped weapons")
        defender_weapon_type = self.defender_weapon.template.weapon_type if self.defender_weapon else None
        # figure out range
        if self.defender_weapon is None:
            self.attacker_outranges_defender = False
        else:
            self.attacker_outranges_defender = \
                not (self.defender_weapon.template.min_range <= at_range <= self.defender_weapon.template.max_range)
        # calculate the core stats for each side
        # Attack Speed
        self.AS_attacker = battle_stats.attack_speed(self.game, self.attacker, self.attacker_weapon)
        self.AS_defender = battle_stats.attack_speed(self.game, self.defender, self.defender_weapon)
        # Hit
        self.hit_attacker = battle_stats.hit(self.arena, self.attacker, self.attacker_weapon,
                                             self.defender, defender_weapon_type)
        if self.attacker_outranges_defender:
            self.hit_defender = 0
        else:
            self.hit_defender = battle_stats.hit(self.arena, self.defender, self.defender_weapon,
                                                 self.attacker, attacker_weapon_type)
        # Avoid
        self.avo_attacker = battle_stats.avoid(self.arena, self.attacker, self.attacker_weapon)
        self.avo_defender = battle_stats.avoid(self.arena, self.defender, self.defender_weapon)
        # Crit
        self.crit_attacker = battle_stats.crit(self.arena, self.attacker, self.attacker_weapon)
        if self.attacker_outranges_defender:
            self.crit_defender = 0
        else:
            self.crit_defender = battle_stats.avoid(self.arena, self.defender, self.defender_weapon)
        # Crit-Avoid
        self.ddg_attacker = battle_stats.dodge(self.arena, self.attacker)
        self.ddg_defender = battle_stats.dodge(self.arena, self.defender)
        # Atk
        self.atk_attacker = battle_stats.attack(self.arena, self.attacker, self.attacker_weapon,
                                                self.defender, defender_weapon_type)
        if self.attacker_outranges_defender:
            self.atk_defender = 0
        else:
            self.atk_defender = battle_stats.attack(self.arena, self.defender, self.defender_weapon,
                                                    self.attacker, self.attacker_weapon.template.weapon_type)
        # Prt / Rsl
        self.prt_attacker = battle_stats.protection(self.arena, self.attacker)
        self.rsl_attacker = battle_stats.resilience(self.arena, self.attacker)
        self.prt_defender = battle_stats.protection(self.arena, self.defender)
        self.rsl_defender = battle_stats.resilience(self.arena, self.defender)
        # battle scene info
        self.displayed_dmg_attacker = max(self.atk_attacker - battle_stats.prt_or_rsl(
            self.defender_weapon.template.damage_type, self.prt_defender, self.rsl_defender), 0)
        self.displayed_dmg_defender = max(self.atk_defender - battle_stats.prt_or_rsl(
            self.attacker_weapon.template.damage_type, self.prt_attacker, self.rsl_attacker), 0)
        self.displayed_hit_attacker = min(max(self.hit_attacker - self.avo_defender, 0), 100)
        self.displayed_hit_defender = min(max(self.hit_defender - self.avo_attacker, 0), 100)
        self.displayed_crit_attacker = min(max(self.crit_attacker - self.ddg_defender, 0), 100)
        self.displayed_crit_defender = min(max(self.crit_defender - self.ddg_attacker, 0), 100)
        # organize preemptive list of attacks
        self.attack_data: AttackData = AttackData(
            by=self.attacker,
            against=self.defender,
            with_weapon=self.attacker_weapon,
            against_weapon=self.defender_weapon,
            atk=self.atk_attacker,
            prt_rsl=battle_stats.prt_or_rsl(self.attacker_weapon.template.damage_type,
                                            self.prt_defender, self.rsl_defender),
            hit=self.hit_attacker,
            avo=self.avo_defender,
            crit=self.crit_attacker,
            ddg=self.ddg_defender,
            counterattack=False,
            followup=False
        )
        self.last_attack = self.attack_data
        # counterattack
        if self.defender_weapon and not self.attacker_outranges_defender:
            self.last_attack = self.last_attack.append(AttackData(
                by=self.defender,
                against=self.attacker,
                with_weapon=self.defender_weapon,
                against_weapon=self.attacker_weapon,
                atk=self.atk_defender,
                prt_rsl=battle_stats.prt_or_rsl(self.defender_weapon.template.damage_type,
                                                self.prt_attacker, self.rsl_attacker),
                hit=self.hit_defender,
                avo=self.avo_attacker,
                crit=self.crit_defender,
                ddg=self.ddg_attacker,
                counterattack=True,
                followup=False
            ))
        # follow-up
        if self.game.follow_up_criteria != FollowUpCriteria.SKILL_ONLY:
            if self.AS_attacker - self.AS_defender >= self.game.follow_up_criteria:
                self.last_attack = self.last_attack.append(AttackData(
                    by=self.attacker,
                    against=self.defender,
                    with_weapon=self.attacker_weapon,
                    against_weapon=self.defender_weapon,
                    atk=self.atk_attacker,
                    prt_rsl=battle_stats.prt_or_rsl(self.attacker_weapon.template.damage_type,
                                                    self.prt_defender, self.rsl_defender),
                    hit=self.hit_attacker,
                    avo=self.avo_defender,
                    crit=self.crit_attacker,
                    ddg=self.ddg_defender,
                    counterattack=False,
                    followup=True
                ))
            elif self.AS_defender - self.AS_attacker >= self.game.follow_up_criteria \
                    and self.defender_weapon and not self.attacker_outranges_defender:
                self.last_attack = self.last_attack.append(AttackData(
                    by=self.defender,
                    against=self.attacker,
                    with_weapon=self.defender_weapon,
                    against_weapon=self.attacker_weapon,
                    atk=self.atk_defender,
                    prt_rsl=battle_stats.prt_or_rsl(self.defender_weapon.template.damage_type,
                                                    self.prt_attacker, self.rsl_attacker),
                    hit=self.hit_defender,
                    avo=self.avo_attacker,
                    crit=self.crit_defender,
                    ddg=self.ddg_attacker,
                    counterattack=True,
                    followup=True
                ))
        # various skills will modify these things.
        # but that should be all for now
        # also, set this to 0 initially
        self.attacker_points = 0
        self.defender_points = 0

    def generate_summary(self) -> Dict:
        """
        :return: a JSON-compatible preemptive summary of the displayed numbers as of the start of
            this combat, comforming to the appropriate subschema in api.arena.schemas
        """
        return {
            "action": "start_combat",
            "attacker": self.attacker.id,
            "attacker_weapon": self.attacker_weapon.id,
            "attacker_displayed_dmg": self.displayed_dmg_attacker,
            "attacker_displayed_hit": self.displayed_hit_attacker,
            "attacker_displayed_crit": self.displayed_crit_attacker,
            "attacker_displayed_atk": self.atk_attacker,
            "attacker_displayed_prt": self.prt_attacker,
            "attacker_displayed_rsl": self.rsl_attacker,
            "defender": self.defender.id,
            "defender_weapon": self.defender_weapon.id if self.defender_weapon else None,
            "defender_displayed_dmg": self.displayed_dmg_defender,
            "defender_displayed_hit": self.displayed_hit_defender,
            "defender_displayed_crit": self.displayed_crit_defender,
            "defender_displayed_atk": self.atk_defender,
            "defender_displayed_prt": self.prt_defender,
            "defender_displayed_rsl": self.rsl_defender,
        }

    def weapon_for_attack(self, attack: AttackData) -> ActiveWeapon:
        """
        Returns the weapon wielded by the unit who made the given attack
        :param attack: AttackData for an attack
        :return: the weapon wielded by the attacker
        """
        if attack.by == self.attacker:
            return self.attacker_weapon
        elif attack.by == self.defender:
            return self.defender_weapon
        else:
            raise ValueError("The attacker is not part of this combat")

    def remove_attack(self, attack: AttackData):
        """
        Removes the given attack from the combat's AttackData.
        :param attack: attack to remove
        """
        if self.attack_data is attack:
            self.attack_data = attack.next
            return
        cur = self.attack_data
        while cur.next:
            if cur.next is attack:
                cur.next = cur.next.next
                break
            cur = cur.next

    def recalculate_from_weapon_changes(self):
        """
        Recalculates most of the combat based on the new weapons being present.
        The Attack Speed of either combatant does not change, and neither does order of attacks.
        """
        defender_weapon_type = self.defender_weapon.template.weapon_type if self.defender_weapon else None
        self.hit_attacker = battle_stats.hit(self.arena, self.attacker, self.attacker_weapon,
                                             self.defender, defender_weapon_type)
        if self.attacker_outranges_defender:
            self.hit_defender = 0
        else:
            self.hit_defender = battle_stats.hit(self.arena, self.defender, self.defender_weapon,
                                                 self.attacker, self.attacker_weapon.template.weapon_type)
        self.avo_attacker = battle_stats.avoid(self.arena, self.attacker, self.attacker_weapon)
        self.avo_defender = battle_stats.avoid(self.arena, self.defender, self.defender_weapon)
        # Crit
        self.crit_attacker = battle_stats.crit(self.arena, self.attacker, self.attacker_weapon)
        if self.attacker_outranges_defender:
            self.crit_defender = 0
        else:
            self.crit_defender = battle_stats.avoid(self.arena, self.defender, self.defender_weapon)
        self.atk_attacker = battle_stats.attack(self.arena, self.attacker, self.attacker_weapon,
                                                self.defender, defender_weapon_type)
        if self.attacker_outranges_defender:
            self.atk_defender = 0
        else:
            self.atk_defender = battle_stats.attack(self.arena, self.defender, self.defender_weapon,
                                                    self.attacker, self.attacker_weapon.template.weapon_type)
        self.displayed_dmg_attacker = max(self.atk_attacker - battle_stats.prt_or_rsl(
            self.defender_weapon.template.damage_type, self.prt_defender, self.rsl_defender), 0)
        self.displayed_dmg_defender = max(self.atk_defender - battle_stats.prt_or_rsl(
            self.attacker_weapon.template.damage_type, self.prt_attacker, self.rsl_attacker), 0)
        self.displayed_hit_attacker = min(max(self.hit_attacker - self.avo_defender, 0), 100)
        self.displayed_hit_defender = min(max(self.hit_defender - self.avo_attacker, 0), 100)
        self.displayed_crit_attacker = min(max(self.crit_attacker - self.ddg_defender, 0), 100)
        self.displayed_crit_defender = min(max(self.crit_defender - self.ddg_attacker, 0), 100)
        for attack in self.attack_data:
            if attack.by == self.attacker:
                attack.with_weapon = self.attacker_weapon
                attack.against_weapon = self.defender_weapon
                attack.atk = self.atk_attacker
                attack.prt_rsl = battle_stats.prt_or_rsl(self.attacker_weapon.template.damage_type, self.prt_defender,
                                                         self.rsl_defender)
                attack.hit = self.hit_attacker
                attack.avo = self.avo_defender
                attack.crit = self.crit_attacker
            elif attack.by == self.defender:
                attack.with_weapon = self.defender_weapon
                attack.against_weapon = self.attacker_weapon
                attack.atk = self.atk_defender
                attack.prt_rsl = battle_stats.prt_or_rsl(self.defender_weapon.template.damage_type, self.prt_attacker,
                                                         self.rsl_attacker)
                attack.hit = self.hit_defender
                attack.avo = self.avo_attacker
                attack.crit = self.crit_defender

    def set_atk_attacker(self, new_atk: int):
        """
        Sets self.atk_attacker based on the new value, and modifies the AttackData accordingly
        :param new_atk: new value for attacker's Atk
        """
        self.atk_attacker = new_atk
        self.displayed_dmg_attacker = max(self.atk_attacker - battle_stats.prt_or_rsl(
            self.defender_weapon.template.damage_type, self.prt_defender, self.rsl_defender), 0)
        for ad in self.attack_data:
            if ad.by == self.attacker:
                ad.atk = new_atk

    def set_atk_defender(self, new_atk: int):
        """
        Sets self.atk_defender based on the new value, and modifies the AttackData accordingly
        :param new_atk: new value for defender's Atk
        """
        if not self.attacker_outranges_defender:
            self.atk_defender = new_atk
            self.displayed_dmg_defender = max(self.atk_defender - battle_stats.prt_or_rsl(
                self.attacker_weapon.template.damage_type, self.prt_attacker, self.rsl_attacker), 0)
            for ad in self.attack_data:
                if ad.by == self.defender:
                    ad.atk = new_atk

    def set_rsl_attacker(self, new_rsl: int):
        """
        Sets self.rsl_attacker based on the new value, and modifies the AttackData accordingly
        :param new_rsl: new value for attacker's Rsl
        """
        self.rsl_attacker = new_rsl
        self.displayed_dmg_defender = max(self.atk_defender - battle_stats.prt_or_rsl(
            self.attacker_weapon.template.damage_type, self.prt_attacker, self.rsl_attacker), 0)
        for ad in self.attack_data:
            if ad.by == self.defender:
                ad.rsl = battle_stats.prt_or_rsl(self.defender_weapon.template.damage_type,
                                                 self.prt_attacker, self.rsl_attacker)

    def set_rsl_defender(self, new_rsl: int):
        """
        Sets self.rsl_Defender based on the new value, and modifies the AttackData accordingly
        :param new_rsl: new value for defender's Rsl
        """
        self.rsl_attacker = new_rsl
        self.displayed_dmg_attacker = max(self.atk_attacker - battle_stats.prt_or_rsl(
            self.defender_weapon.template.damage_type, self.prt_defender, self.rsl_defender), 0)
        for ad in self.attack_data:
            if ad.by == self.attacker:
                ad.rsl = battle_stats.prt_or_rsl(self.attacker_weapon.template.damage_type,
                                                 self.prt_defender, self.rsl_defender)

    def set_hit_attacker(self, new_hit: int):
        """
        Sets self.hit_attacker based on the new value, and modifies the AttackData accordingly
        :param new_hit: new value for attacker's Hit
        """
        self.hit_attacker = new_hit
        self.displayed_hit_attacker = min(max(self.hit_attacker - self.avo_defender, 0), 100)
        for ad in self.attack_data:
            if ad.by == self.attacker:
                ad.hit = new_hit

    def set_hit_defender(self, new_hit: int):
        """
        Sets self.hit_defender based on the new value, and modifies the AttackData accordingly
        :param new_hit: new value for defender's Hit
        """
        self.hit_defender = new_hit
        self.displayed_hit_defender = min(max(self.hit_defender - self.avo_attacker, 0), 100)
        for ad in self.attack_data:
            if ad.by == self.defender:
                ad.hit = new_hit

    def set_crit_attacker(self, new_crit: int):
        """
        Sets self.crit_attacker based on the new value, and modifies the AttackData accordingly
        :param new_crit: new value for attacker's Crit
        """
        self.crit_attacker = new_crit
        self.displayed_crit_attacker = min(max(self.crit_attacker - self.ddg_defender, 0), 100)
        for ad in self.attack_data:
            if ad.by == self.attacker:
                ad.crit = new_crit

    def set_crit_defender(self, new_crit: int):
        """
        Sets self.crit_defender based on the new value, and modifies the AttackData accordingly
        :param new_crit: new value for defender's Crit
        """
        self.crit_defender = new_crit
        self.displayed_crit_defender = min(max(self.crit_defender - self.ddg_attacker, 0), 100)
        for ad in self.attack_data:
            if ad.by == self.defender:
                ad.crit = new_crit

    def set_ddg_attacker(self, new_ddg: int):
        """
        sets self.ddg_attacker based on the new value, and modifies AttackData accordingly
        :param new_ddg: new value for attacker's Ddg
        """
        self.ddg_attacker = new_ddg
        self.displayed_crit_defender = min(max(self.crit_defender - self.ddg_attacker, 0), 100)
        for ad in self.attack_data:
            if ad.against == self.attacker:
                ad.ddg = new_ddg

    def set_ddg_defender(self, new_ddg: int):
        """
        sets self.ddg_defender based on the new value, and modifies AttackData accordingly
        :param new_ddg: new value for defender's Ddg
        """
        self.ddg_defender = new_ddg
        self.displayed_crit_attacker = min(max(self.crit_attacker - self.ddg_defender, 0), 100)
        for ad in self.attack_data:
            if ad.against == self.defender:
                ad.ddg = new_ddg


class AfterAttackData:
    """
    A class mainly to represent data from after a particular attack, for the
    benefit of skills that execute after making an attack or after being
    attacked. This essentially conforms to the 'attack' subschema of the
    action_output_schema (see api.arena.schemas)
    """

    def __init__(self, by: ActiveUnit, weapon: ActiveWeapon, against: ActiveUnit,
                 miss: bool, crit: bool, dmg: int, tags: List[str]):
        self.by = by
        self.weapon = weapon
        self.against = against
        self.miss = miss
        self.crit = crit
        self.dmg = dmg
        self.tags = tags

    def to_dict(self):
        return {
            "action": "attack",
            "by_unit": self.by.id,
            "weapon": self.weapon.id,
            "against_unit": self.against.id,
            "miss": self.miss,
            "skills": self.tags,
            "crit": self.crit,
            "dmg": self.dmg
        }
