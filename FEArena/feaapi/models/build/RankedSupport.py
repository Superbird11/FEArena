from django.db import models
from .._util import BaseModel
from .BuiltUnit import BuiltUnit
from ..core.Unit import Unit
from ..core.Game import SupportRank


class RankedSupport(BaseModel):
    # two of these will exist for a single support between two units
    # one for each direction
    unit: BuiltUnit = models.ForeignKey(BuiltUnit, on_delete=models.CASCADE)
    supported_by: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    rank: int = models.IntegerField(choices=SupportRank.choices)

    def to_json(self):
        """
        Returns a JSON-compatible representation of this ranked support
        """
        return {
            "unit": self.unit.id,
            "supported_by": self.supported_by.id,
            "rank": self.rank
        }
