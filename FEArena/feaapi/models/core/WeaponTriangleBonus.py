from django.db import models
from .._util import BaseModel, maxlength
from .Game import FireEmblemGame
from .WeaponRank import WeaponRank


class WeaponTriangleBonus(BaseModel):
    # Note: for games that don't give different weapon triangle bonuses based on level,
    # it is still expected that the database has info for all applicable levels (i.e.
    # identical records for E, D, C, B, A, S, SS)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    weapon_rank: str = models.CharField(choices=WeaponRank.choices,
                                        max_length=maxlength(WeaponRank))

    atk_bonus: int = models.IntegerField(default=0)
    hit_bonus: int = models.IntegerField(default=0)

    class Meta:
        unique_together = ('game', 'weapon_rank')

    def __str__(self):
        return f"{self.game.abbrev} - Rank {self.weapon_rank}: +{self.atk_bonus} atk, +{self.hit_bonus} hit"
