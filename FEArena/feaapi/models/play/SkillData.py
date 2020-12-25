from django.db import models
from .._util import BaseModel
from .ActiveArena import ActiveArena
from .ActiveUnit import ActiveUnit
from ..core.Skill import Skill


class SkillData(BaseModel):
    # identifying factors for individual skills
    arena: ActiveArena = models.ForeignKey(ActiveArena, on_delete=models.CASCADE)
    unit: ActiveUnit = models.ForeignKey(ActiveUnit, on_delete=models.CASCADE)
    skill: Skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    # skills can use this data however they need to
    data_bool: bool = models.BooleanField(null=True, blank=True)
    data_int1: int = models.IntegerField(null=True, blank=True)
    data_int2: int = models.IntegerField(null=True, blank=True)
    data_str1: str = models.CharField(null=True, blank=True, max_length=64)
    data_str2: str = models.CharField(null=True, blank=True, max_length=64)

    class Meta:
        unique_together = (('arena', 'unit', 'skill'),)
