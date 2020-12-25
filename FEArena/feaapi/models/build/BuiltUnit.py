from django.db import models
from typing import Dict
from .._util import BaseModel, maxlength
from ..core.Skill import Skill
from ..core.Class import Class
from ..core.Unit import Unit
from ..core.Weapon import WeaponType
from .BuiltClass import BuiltClass
from .BuiltWeapon import BuiltWeapon
from .BuiltItem import BuiltItem


class BuiltUnit(BaseModel):
    # personal information
    id: int = models.AutoField(primary_key=True)
    nickname: str = models.CharField(max_length=255)

    # base build information
    unit: Unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    unit_class: Class = models.ForeignKey(Class, on_delete=models.PROTECT)
    unit_level: int = models.IntegerField(default=20)
    unit_class_history = models.ManyToManyField(BuiltClass)  # should include current class
    from_instructions: Dict = models.JSONField(null=False)
    main_weapon_type: str = models.CharField(choices=WeaponType.choices, null=True, blank=True,
                                             max_length=maxlength(WeaponType))
    validated: bool = models.BooleanField(default=True)
    limited: bool = models.BooleanField(default=True)

    # custom build information - what has been added to this character?
    boosts_hp: int = models.IntegerField(default=0)
    boosts_str: int = models.IntegerField(default=0)
    boosts_mag: int = models.IntegerField(default=0, null=True, blank=True)
    boosts_skl: int = models.IntegerField(default=0)
    boosts_spd: int = models.IntegerField(default=0)
    boosts_luk: int = models.IntegerField(default=0)
    boosts_def: int = models.IntegerField(default=0)
    boosts_res: int = models.IntegerField(default=0)
    boosts_cha: int = models.IntegerField(default=0)
    boosts_con: int = models.IntegerField(default=0)
    boosts_mov: int = models.IntegerField(default=0)

    # weapon ranks
    boost_rank_sword: int = models.IntegerField(default=0)
    boost_rank_lance: int = models.IntegerField(default=0)
    boost_rank_axe: int = models.IntegerField(default=0)
    boost_rank_bow: int = models.IntegerField(default=0)
    boost_rank_gauntlet: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_hidden: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_tome: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_fire: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_wind: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_thunder: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_dark: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_light: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_anima: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_black: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_white: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_staff: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_dragonstone: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_beast: int = models.IntegerField(default=0, null=True, blank=True)
    boost_rank_special: int = models.IntegerField(default=0, null=True, blank=True)

    # equippables
    weapons = models.ManyToManyField(BuiltWeapon)
    items = models.ManyToManyField(BuiltItem)
    extra_skills = models.ManyToManyField(Skill)

    def to_dict(self):
        """
        :return: a JSON-compatible representation of this BuiltUnit, conforming to the appropriate
            schema in api.teambuilder.schemas
        """
        return {
            "id": self.id,
            "nickname": self.nickname,
            "base_unit": self.unit.to_dict(),
            "class": self.unit_class.to_dict(),
            "level": self.unit_level,
            "class_history": [
                {"class": cls.template.to_dict(), "levels": cls.levels} for cls in self.unit_class_history.all()
            ],
            "main_weapon_type": self.main_weapon_type,
            "validated": self.validated,
            "limited": self.limited,
            "stat_boosts": {
                "hp": self.boosts_hp,
                "str": self.boosts_str,
                "mag": self.boosts_mag,
                "skl": self.boosts_skl,
                "spd": self.boosts_spd,
                "luk": self.boosts_luk,
                "def": self.boosts_def,
                "res": self.boosts_res,
                "cha": self.boosts_cha,
                "mov": self.boosts_mov,
                "con": self.boosts_con,
            },
            "rank_boosts": {
                WeaponType.SWORD: self.boost_rank_sword,
                WeaponType.LANCE: self.boost_rank_lance,
                WeaponType.AXE: self.boost_rank_axe,
                WeaponType.BOW: self.boost_rank_bow,
                WeaponType.GAUNTLET: self.boost_rank_gauntlet,
                WeaponType.HIDDEN: self.boost_rank_hidden,
                WeaponType.TOME: self.boost_rank_tome,
                WeaponType.FIRE: self.boost_rank_fire,
                WeaponType.THUNDER: self.boost_rank_thunder,
                WeaponType.WIND: self.boost_rank_wind,
                WeaponType.LIGHT: self.boost_rank_light,
                WeaponType.DARK: self.boost_rank_dark,
                WeaponType.ANIMA: self.boost_rank_anima,
                WeaponType.BLACK: self.boost_rank_black,
                WeaponType.WHITE: self.boost_rank_white,
                WeaponType.STAFF: self.boost_rank_staff,
                WeaponType.DRAGONSTONE: self.boost_rank_dragonstone,
                WeaponType.BEAST: self.boost_rank_beast,
                WeaponType.SPECIAL: self.boost_rank_special,
            },
            "weapons": [weapon.to_dict() for weapon in self.weapons.all()],
            "items": [item.to_dict() for item in self.items.all()],
            "extra_skills": [skill.to_dict() for skill in self.extra_skills.all()],
            "instructions": self.from_instructions
        }
