from django.db import models
from .._util import BaseModel
from ..core.Weapon import Weapon
from ..build.BuiltWeapon import BuiltWeapon


class ActiveWeapon(BaseModel):
    id: int = models.AutoField(primary_key=True)
    inventory_id: int = models.IntegerField(default=0)
    template: Weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    equipped: bool = models.BooleanField(default=False)
    uses: int = models.IntegerField(default=-1)

    def to_dict(self):
        """
        :return: a representation of this ActiveWeapon in JSON, conforming to the active_weapon_schema
            defined in api.arena.schemas
        """
        return {
            'id': self.id,
            'name': self.template.name,
            'game': self.template.game.name,
            'description': self.template.description,
            'inventory_id': self.inventory_id,
            'damage_type': self.template.damage_type,
            'weapon_type': self.template.weapon_type,
            'rank': self.template.rank,
            'prf': [unit.name for unit in self.template.prf_users.all()],
            'mt': self.template.mt,
            'hit': self.template.hit,
            'crit': self.template.crit,
            'min_range': self.template.min_range,
            'max_range': self.template.max_range,
            'wt': self.template.wt,
            'total_uses': self.template.uses,
            'current_uses': self.uses,
            'usable': self.template.usable,
            'equipped': self.equipped,
            'skills': [skill.to_dict() for skill in self.template.weapon_effects.all()]
        }

    @staticmethod
    def from_BuiltWeapon(weapon: BuiltWeapon) -> 'ActiveWeapon':
        """
        Creates, saves, and returns a new ActiveWeapon initialized from the given Weapon as a template
        """
        active_weapon = ActiveWeapon.objects.create(
            template=weapon.template,
            uses=weapon.template.uses,
            inventory_id=weapon.inventory_id,
            equipped=weapon.equipped
        )
        return active_weapon
