from django.db import models


class BaseModel(models.Model):
    """
    Abstract class model with an explicit .object property
    literally for no other reason than to make the autoformatter
    shut up
    """
    objects = models.Manager()

    class Meta:
        abstract = True


def maxlength(cls):
    return len(max(cls.choices, key=lambda k: len(k[0]))[0])
