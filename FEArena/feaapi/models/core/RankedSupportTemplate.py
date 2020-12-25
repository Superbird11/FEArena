from django.db import models
from .._util import BaseModel
from .Unit import Unit
from .Game import SupportRank


class RankedSupportTemplate(BaseModel):
    unit: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='_ranked_supported_by_set')
    supported_by: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='_ranked_supports_set')
    max_rank: int = models.IntegerField(choices=SupportRank.choices, default=SupportRank.A)
    default_rank: int = models.IntegerField(choices=SupportRank.choices, default=SupportRank.NONE)

    hit_c: int = models.IntegerField(default=0)
    hit_b: int = models.IntegerField(default=0)
    hit_a: int = models.IntegerField(default=0)
    hit_s: int = models.IntegerField(default=0)
    crit_c: int = models.IntegerField(default=0)
    crit_b: int = models.IntegerField(default=0)
    crit_a: int = models.IntegerField(default=0)
    crit_s: int = models.IntegerField(default=0)
    avo_c: int = models.IntegerField(default=0)
    avo_b: int = models.IntegerField(default=0)
    avo_a: int = models.IntegerField(default=0)
    avo_s: int = models.IntegerField(default=0)
    ddg_c: int = models.IntegerField(default=0)
    ddg_b: int = models.IntegerField(default=0)
    ddg_a: int = models.IntegerField(default=0)
    ddg_s: int = models.IntegerField(default=0)

    def __str__(self):
        return f"{str(self.unit)} <-- {str(self.supported_by)} (default {self.default_rank}; max {self.max_rank})"
