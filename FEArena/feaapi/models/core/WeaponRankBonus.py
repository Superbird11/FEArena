from django.db import models
from .._util import BaseModel, maxlength
from .Game import FireEmblemGame
from .Weapon import WeaponType
from .WeaponRank import WeaponRank


class WeaponRankBonus(BaseModel):
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    weapon_type: str = models.CharField(choices=WeaponType.choices,
                                        max_length=maxlength(WeaponType))
    weapon_rank: str = models.CharField(choices=WeaponRank.choices,
                                        max_length=maxlength(WeaponType))

    atk_bonus: int = models.IntegerField(default=0)
    hit_bonus: int = models.IntegerField(default=0)
    crit_bonus: int = models.IntegerField(default=0)
    recovery_bonus: int = models.IntegerField(default=0)

    class Meta:
        unique_together = ('game', 'weapon_type', 'weapon_rank')

    def __str__(self):
        return f"{self.game.abbrev} - {self.weapon_rank} {self.weapon_type}s"
