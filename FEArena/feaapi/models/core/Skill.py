from django.db import models
from .._util import BaseModel
from typing import Dict
from .Game import FireEmblemGame


class Skill(BaseModel):
    id: int = models.IntegerField(primary_key=True)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=255)
    description: str = models.CharField(max_length=255)
    priority: int = models.IntegerField(default=0)  # higher priority -> will activate first, when order matters
    cost: int = models.IntegerField(default=0)  # FE9, FE10

    build_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Shadowgift; at build-time
    passive_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. stat-plus skills
    before_combat_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Vantage
    after_combat_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Poison Strike
    before_attack_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Luna
    after_attack_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Sol
    before_attacked_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Pavise
    after_attacked_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Counter
    turn_start_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Renewal
    unit_turn_end_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Canto, Lifetaker, 'on Wait' skills
    turn_end_effect: str = models.CharField(null=True, blank=True, max_length=64)  # Mostly used to turn off previous effects
    on_use_effect: str = models.CharField(null=True, blank=True, max_length=64)  # e.g. Dance, Rally, etc.
    on_equip_effect: str = models.CharField(null=True, blank=True, max_length=64)  # for equippable items
    on_dequip_effect: str = models.CharField(null=True, blank=True, max_length=64)  # for reversing the on_equip effects

    invisible: bool = models.BooleanField(default=False)

    def to_dict(self) -> Dict:
        """
        :return: a representation of this skill in JSON, conforming to the skill_schema defined
        in api.arena.schemas
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game': self.game.name,
            'priority': self.priority,
            'effects': {
                'passive': self.passive_effect,
                'before_combat': self.before_combat_effect,
                'after_combat': self.after_combat_effect,
                'before_attack': self.before_attack_effect,
                'after_attack': self.after_attack_effect,
                'before_attacked': self.before_attacked_effect,
                'after_attacked': self.after_attacked_effect,
                'turn_start': self.turn_start_effect,
                'turn_end': self.turn_end_effect,
                'use': self.on_use_effect,
                'equip': self.on_equip_effect,
                'dequip': self.on_dequip_effect,
            }
        }

    def __str__(self):
        if self.id >= 100:
            return f"{self.game.abbrev}!{self.name} ({self.id})"
        else:
            return f"{self.name} ({self.id})"

