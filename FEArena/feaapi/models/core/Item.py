from django.db import models
from .._util import BaseModel
from .Unit import Unit
from .Game import FireEmblemGame
from .Skill import Skill


class Item(BaseModel):
    # demographic information
    id: int = models.IntegerField(primary_key=True)
    name: str = models.CharField(max_length=255)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=255)
    prf_users = models.ManyToManyField(Unit)

    # item properties
    wt: int = models.IntegerField(default=0)
    uses: int = models.IntegerField(default=-1)
    usable: bool = models.BooleanField(default=True)
    equippable: bool = models.BooleanField(default=False)
    item_effects = models.ManyToManyField(Skill)

    # Some items confer skills, e.g. the Return Ring, that are used by selecting those 'skills'
    # on the battlefield rather than by selecting the item to use. In every such case, the item
    # itself may be equippable but is not directly usable. In such a case, the command_name should
    # be provided, giving the name of the battlefield command (e.g. 'Return'). This will supersede
    # the 'usable' quality, and trigger the `on_use` item effects if activated.
    command_name: str = models.CharField(null=True, blank=True, max_length=32)

    def to_dict(self):
        """
        :return: a JSON-compatible representation of this Item, conforming to the appropriate
            schema in api.teambuilder.schemas
        """
        return {
            'id': self.id,
            'name': self.name,
            'game': self.game.abbrev,
            'description': self.description,
            'prf_users': [unit.id for unit in self.prf_users.all()],
            'wt': self.wt,
            'uses': self.uses,
            'usable': self.usable,
            'equippable': self.equippable,
            'command': self.command_name,
            'effects': [skill.to_dict() for skill in self.item_effects.all()]
        }

    def __str__(self):
        return f"{self.game.abbrev}!{self.name} ({self.id})"
