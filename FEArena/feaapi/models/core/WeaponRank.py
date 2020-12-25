from django.db import models
from .._util import BaseModel, maxlength
from .Game import FireEmblemGame, WeaponRank


class WeaponRankPointRequirement(BaseModel):
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    weapon_rank: str = models.CharField(choices=WeaponRank.choices, max_length=maxlength(WeaponRank))
    points_required: int = models.IntegerField(default=0)

    class Meta:
        unique_together = ('game', 'weapon_rank')

    def __str__(self):
        return f"{self.game} - {self.weapon_rank} ({self.points_required}"
