from django.db import models
from .._util import BaseModel
from ..core.Item import Item


class BuiltItem(BaseModel):
    template: Item = models.ForeignKey(Item, on_delete=models.CASCADE)
    inventory_id: int = models.IntegerField(default=0)
    equipped: bool = models.BooleanField(default=False)

    def to_dict(self):
        """
        :return: a JSON-compliant representation of this BuiltItem, conforming to
            the appropriate schema from api.teambuilder.schemas
        """
        return {
            **self.template.to_dict(),
            "equipped": self.equipped,
            "inventory_id": self.inventory_id,
        }
