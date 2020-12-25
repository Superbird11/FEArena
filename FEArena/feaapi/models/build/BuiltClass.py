from django.db import models
from .._util import BaseModel
from ..core.Class import Class


class BuiltClass(BaseModel):
    template: Class = models.ForeignKey(Class, on_delete=models.CASCADE)
    levels: int = models.IntegerField(default=0)
