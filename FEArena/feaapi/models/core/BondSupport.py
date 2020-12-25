from django.db import models
from .._util import BaseModel
from .Unit import Unit


class BondSupport(BaseModel):
    unit: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="_bond_supported_by_obj")
    supported_by: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="_bond_supports_obj")
    strength: int = models.IntegerField(default=0)

    # future-proofing. Either Strength is used, or this, depending on game
    hit_bonus: int = models.IntegerField(default=0)
    crit_bonus: int = models.IntegerField(default=0)
    avo_bonus: int = models.IntegerField(default=0)
    ddg_bonus: int = models.IntegerField(default=0)

    def to_json(self):
        """
        Returns a JSON-compatible representation of this BondSupport, conforming to the
        appropriate schema in api.teambuilder.schemas
        """
        return {
            "unit": self.unit.id,
            "supported_by": self.supported_by.id,
            "strength": self.strength,
            "bonuses": {
                "hit": self.hit_bonus,
                "crit": self.crit_bonus,
                "avo": self.avo_bonus,
                "ddg": self.ddg_bonus
            }
        }

    def __str__(self):
        return f"{str(self.unit)} <-- {str(self.supported_by)}"
