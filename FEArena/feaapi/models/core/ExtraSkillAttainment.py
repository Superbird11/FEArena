from django.db import models
from .._util import BaseModel
from . import Class
from . import Skill


class ExtraSkill(BaseModel):
    unit_class: Class = models.ForeignKey(Class, on_delete=models.CASCADE)
    skill: Skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level: int = models.IntegerField(default=1)

    def __str__(self):
        return f"{str(self.unit_class)} Lv. {self.level} - {str(self.skill)}"
