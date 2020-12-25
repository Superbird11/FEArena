from django.db import models
from .._util import BaseModel, maxlength
from ..core.Game import FireEmblemGame


class VictoryCondition(models.TextChoices):
    SURVIVAL = 'Survival'
    POINTS = 'Points'


class GameFormat(BaseModel):
    name: str = models.CharField(primary_key=True, max_length=255)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    validated: bool = models.BooleanField(default=True)
    victory: str = models.CharField(choices=VictoryCondition.choices, default=VictoryCondition.POINTS,
                                    max_length=maxlength(VictoryCondition))
