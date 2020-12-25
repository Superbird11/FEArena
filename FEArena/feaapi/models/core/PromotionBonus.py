from django.db import models
from .._util import BaseModel
from . import Class


# This should be relative to the class bonuses at play.
# e.g. if the class base for the unpromoted class is 4, and the class base for the promoted class is 3,
# but the ingame promotion bonus is +3, then this should be +4 to achieve the same result
class PromotionBonus(BaseModel):
    from_class: Class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='_promotion_set')
    to_class: Class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='_promoted_set')

    bonus_hp: int = models.IntegerField(default=0)
    bonus_str: int = models.IntegerField(default=0)
    bonus_mag: int = models.IntegerField(default=0)
    bonus_skl: int = models.IntegerField(default=0)
    bonus_spd: int = models.IntegerField(default=0)
    bonus_luk: int = models.IntegerField(default=0)
    bonus_def: int = models.IntegerField(default=0)
    bonus_res: int = models.IntegerField(default=0)
    bonus_con: int = models.IntegerField(default=0)
    bonus_mov: int = models.IntegerField(default=0)
    bonus_cha: int = models.IntegerField(default=0)

    bonus_sword: int = models.IntegerField(default=0)
    bonus_lance: int = models.IntegerField(default=0)
    bonus_axe: int = models.IntegerField(default=0)
    bonus_bow: int = models.IntegerField(default=0)
    bonus_gauntlet: int = models.IntegerField(default=0)
    bonus_hidden: int = models.IntegerField(default=0)
    bonus_fire: int = models.IntegerField(default=0)
    bonus_thunder: int = models.IntegerField(default=0)
    bonus_wind: int = models.IntegerField(default=0)
    bonus_dark: int = models.IntegerField(default=0)
    bonus_light: int = models.IntegerField(default=0)
    bonus_anima: int = models.IntegerField(default=0)
    bonus_tome: int = models.IntegerField(default=0)
    bonus_black: int = models.IntegerField(default=0)
    bonus_white: int = models.IntegerField(default=0)
    bonus_staff: int = models.IntegerField(default=0)
    bonus_dragonstone: int = models.IntegerField(default=0)
    bonus_beast: int = models.IntegerField(default=0)
    bonus_other: int = models.IntegerField(default=0)

    class Meta:
        unique_together = (('from_class', 'to_class'),)

    def __str__(self):
        return f"{str(self.from_class)} --> {str(self.to_class)}"
