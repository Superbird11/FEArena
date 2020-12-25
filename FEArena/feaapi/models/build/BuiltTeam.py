from django.db import models
from .._util import BaseModel
from django.contrib.auth.models import User
from .BuiltUnit import BuiltUnit
from ..core.Unit import Affinity


class BuiltTeam(BaseModel):
    id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(default='Untitled', max_length=255)
    units = models.ManyToManyField(BuiltUnit)
    owned_by: User = models.ForeignKey(User, on_delete=models.CASCADE)
    tactician_affinity: str = models.CharField(null=True, blank=True, max_length=7)
    tactician_rank: int = models.IntegerField(null=True, blank=True)

    def to_dict(self):
        """
        :return: a JSON-compatible representation of this BuiltTeam, conforming to the
            appropriateschema in api.teambuilder.schemas
        """
        return {
            "id": self.id,
            "owner": self.owned_by.username,
            "name": self.name,
            "units": [unit.to_dict() for unit in self.units.all()],
            "tactician_rank": {
                "affinity": self.tactician_affinity,
                "rank": self.tactician_rank
            }
        }

    def __str__(self):
        return f"{self.id} - {self.name} ({self.owned_by.username})"
