from django.db import models
from .._util import BaseModel
from ..build.BuiltTeam import BuiltTeam
from .ActiveUnit import ActiveUnit


class ActiveTeam(BaseModel):
    id: int = models.AutoField(primary_key=True)
    template: BuiltTeam = models.ForeignKey(BuiltTeam, on_delete=models.CASCADE)
    units = models.ManyToManyField(ActiveUnit)
    score: int = models.IntegerField(default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.template.owned_by.username,
            'name': self.template.name,
            'units': [
                unit.to_dict() for unit in self.units.all()
            ],
            'score': self.score
        }
