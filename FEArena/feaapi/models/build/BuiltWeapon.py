from django.db import models
from .._util import BaseModel
from ..core.Weapon import Weapon


class BuiltWeapon(BaseModel):
    template: Weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    equipped: bool = models.BooleanField(default=False)
    inventory_id: int = models.IntegerField(default=0)

    def to_dict(self):
        """
        :return: a JSON-compliant representation of this BuiltWeapon, conforming to
            the appropriate schema from api.teambuilder.schemas
        """
        return {
            **self.template.to_dict(),
            "equipped": self.equipped,
            "inventory_id": self.inventory_id,
        }