from django.db import models
from .._util import BaseModel
from ..core.Item import Item
from ..build.BuiltItem import BuiltItem


class ActiveItem(BaseModel):
    id: int = models.AutoField(primary_key=True)
    template: Item = models.ForeignKey(Item, on_delete=models.CASCADE)
    equipped: bool = models.BooleanField(default=False)
    uses: int = models.IntegerField(default=-1)
    inventory_id: int = models.IntegerField(default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.template.name,
            'game': self.template.game.name,
            'description': self.template.description,
            'inventory_id': self.inventory_id,
            'prf': [unit.name for unit in self.template.prf_users.all()],
            'wt': self.template.wt,
            'total_uses': self.template.uses,
            'current_uses': self.uses,
            'usable': self.template.usable,
            'equippable': self.template.equippable,
            'equipped': self.equipped,
            'skills': [skill.to_dict() for skill in self.template.item_effects.all()]
        }

    @staticmethod
    def from_BuiltItem(item: BuiltItem) -> 'ActiveItem':
        """
        Creates, saves, and returns a new ActiveItem initialized from the given Item as a template
        """
        active_item = ActiveItem.objects.create(
            template=item.template,
            uses=item.template.uses,
            inventory_id=item.inventory_id,
            equipped=item.equipped,
        )
        return active_item

