from django.db import models
from .._util import BaseModel, maxlength
from .WeaponRank import WeaponRank
from .WeaponType import WeaponType
from .Unit import Unit
from .Game import FireEmblemGame
from .Skill import Skill


class WeaponDamageType(models.TextChoices):
    PHYSICAL = 'Physical'
    MAGICAL = 'Magical'
    FIXED = 'Fixed'


class Weapon(BaseModel):
    # demographic info
    id: int = models.IntegerField(primary_key=True)
    name: str = models.CharField(max_length=255)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=255)
    damage_type: str = models.CharField(choices=WeaponDamageType.choices, max_length=maxlength(WeaponDamageType))
    weapon_type: str = models.CharField(choices=WeaponType.choices, max_length=maxlength(WeaponType))
    breaks_into: 'Weapon' = models.ForeignKey('Weapon', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    # usage info
    rank: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.E,
                                 max_length=maxlength(WeaponRank))
    prf_users = models.ManyToManyField(Unit)
    mt: int = models.IntegerField(default=1)
    hit: int = models.IntegerField(default=100)
    crit: int = models.IntegerField(default=0)
    min_range: int = models.IntegerField(default=1)
    max_range: int = models.IntegerField(default=1)
    wt: int = models.IntegerField(default=0)
    uses: int = models.IntegerField(default=-1)
    usable: bool = models.BooleanField(default=False)  # can be used like an item with the 'Use' command, e.g. Falchion

    # special effects, if any
    weapon_effects = models.ManyToManyField(Skill)

    def to_dict(self):
        """
        :return: a JSON-compatible representation of this Weapon, conforming to the appropriate
            schema in api.teambuilder.schemas
        """
        return {
            'id': self.id,
            'name': self.name,
            'game': self.game.abbrev,
            'description': self.description,
            'damage_type': self.damage_type,
            'weapon_type': self.weapon_type,
            'breaks_into': self.breaks_into.id if self.breaks_into else None,
            'rank': self.rank,
            'prf_users': [unit.id for unit in self.prf_users.all()],
            'mt': self.mt,
            'hit': self.hit,
            'crit': self.crit,
            'min_range': self.min_range,
            'max_range': self.max_range,
            'wt': self.wt,
            'uses': self.uses,
            'usable': self.usable,
            'effects': [skill.to_dict() for skill in self.weapon_effects.all()]
        }

    def __str__(self):
        return f"{self.game.abbrev}!{self.name} ({self.id})"
