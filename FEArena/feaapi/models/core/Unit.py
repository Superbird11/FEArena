from django.db import models
from .._util import BaseModel, maxlength
from .Game import FireEmblemGame, FireEmblemGameRoute
from .Class import Class
from .Skill import Skill
from .Weapon import WeaponType
# from .BondSupport import BondSupport


class UnitSex(models.TextChoices):
    SEX_MALE = 'M'
    SEX_FEMALE = 'F'
    SEX_OTHER = 'X'


class Affinity(models.TextChoices):
    ANIMA = 'Anima'
    LIGHT = 'Light'
    DARK = 'Dark'
    FIRE = 'Fire'
    THUNDER = 'Thunder'
    WIND = 'Wind'
    ICE = 'Ice'
    WATER = 'Water'
    EARTH = 'Earth'
    HEAVEN = 'Heaven'


# Base stats and growths should be input relative to the class bases and growths
# for the game in question. For example in FE7, if the unit's growth is 55% but the class's
# growth is 70%, set unit's growth to -15%.
# For FE7 in particular, class growths have been set to 0. Bases follow the principle, though.
# This is a quirk of data entry.
class Unit(BaseModel):
    # intrinsic characteristics
    id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(max_length=255)
    description: str = models.CharField(default='', max_length=255)
    sex: str = models.CharField(max_length=1, choices=UnitSex.choices)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    route: FireEmblemGameRoute = models.ForeignKey(FireEmblemGameRoute, on_delete=models.SET_NULL,
                                                   null=True, blank=True, default=None)
    initial_class: Class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='+')
    base_classes = models.ManyToManyField(Class)
    affinity: str = models.CharField(choices=Affinity.choices, null=True, blank=True,
                                     max_length=maxlength(Affinity))

    # supports
    bond_supports = models.ManyToManyField("self", through='BondSupport', through_fields=('unit', 'supported_by'),
                                           symmetrical=False)
    can_ranked_support = models.ManyToManyField('self')

    # personal base stats (not class)
    base_lv: int = models.IntegerField(default=1)
    base_hp: int = models.IntegerField(default=10)
    base_str: int = models.IntegerField(default=0)
    base_mag: int = models.IntegerField(default=0)
    base_skl: int = models.IntegerField(default=0)
    base_spd: int = models.IntegerField(default=0)
    base_luk: int = models.IntegerField(default=0)
    base_def: int = models.IntegerField(default=0)
    base_res: int = models.IntegerField(default=0)
    base_cha: int = models.IntegerField(default=0)
    base_con: int = models.IntegerField(default=1)
    base_mov: int = models.IntegerField(default=4)

    # personal growths
    growth_hp: int = models.IntegerField(default=0)
    growth_str: int = models.IntegerField(default=0)
    growth_mag: int = models.IntegerField(default=0)
    growth_skl: int = models.IntegerField(default=0)
    growth_spd: int = models.IntegerField(default=0)
    growth_luk: int = models.IntegerField(default=0)
    growth_def: int = models.IntegerField(default=0)
    growth_res: int = models.IntegerField(default=0)
    growth_cha: int = models.IntegerField(default=0)
    growth_con: int = models.IntegerField(default=0)
    growth_mov: int = models.IntegerField(default=0)

    # personal max stats
    max_hp: int = models.IntegerField(default=-1)
    max_str: int = models.IntegerField(default=-1)
    max_mag: int = models.IntegerField(default=-1)
    max_skl: int = models.IntegerField(default=-1)
    max_spd: int = models.IntegerField(default=-1)
    max_luk: int = models.IntegerField(default=-1)
    max_def: int = models.IntegerField(default=-1)
    max_res: int = models.IntegerField(default=-1)
    max_cha: int = models.IntegerField(default=-1)
    max_con: int = models.IntegerField(default=-1)
    max_mov: int = models.IntegerField(default=-1)

    # personal max stat modifiers
    mod_max_hp: int = models.IntegerField(default=0)
    mod_max_str: int = models.IntegerField(default=0)
    mod_max_mag: int = models.IntegerField(default=0)
    mod_max_skl: int = models.IntegerField(default=0)
    mod_max_spd: int = models.IntegerField(default=0)
    mod_max_luk: int = models.IntegerField(default=0)
    mod_max_def: int = models.IntegerField(default=0)
    mod_max_res: int = models.IntegerField(default=0)
    mod_max_cha: int = models.IntegerField(default=0)
    mod_max_con: int = models.IntegerField(default=0)
    mod_max_mov: int = models.IntegerField(default=0)

    # personal base weapon ranks
    # in points
    base_rank_sword: int = models.IntegerField(default=0)
    base_rank_lance: int = models.IntegerField(default=0)
    base_rank_axe: int = models.IntegerField(default=0)
    base_rank_bow: int = models.IntegerField(default=0)
    base_rank_gauntlet: int = models.IntegerField(default=0)
    base_rank_hidden: int = models.IntegerField(default=0)
    base_rank_tome: int = models.IntegerField(default=0)
    base_rank_fire: int = models.IntegerField(default=0)
    base_rank_wind: int = models.IntegerField(default=0)
    base_rank_thunder: int = models.IntegerField(default=0)
    base_rank_dark: int = models.IntegerField(default=0)
    base_rank_light: int = models.IntegerField(default=0)
    base_rank_anima: int = models.IntegerField(default=0)
    base_rank_black: int = models.IntegerField(default=0)
    base_rank_white: int = models.IntegerField(default=0)
    base_rank_staff: int = models.IntegerField(default=0)
    base_rank_dragonstone: int = models.IntegerField(default=0)
    base_rank_beast: int = models.IntegerField(default=0)
    base_rank_special: int = models.IntegerField(default=0)

    # other data
    personal_skills = models.ManyToManyField(Skill)
    skill_tolerance: int = models.IntegerField(default=0)

    def to_dict(self):
        """
        :return: A JSON-compatible representation of this Unit conforming to the appropriate
            schema in api.teambuilder.schemas.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sex': self.sex,
            'game': self.game.abbrev,
            'route': self.route.name if self.route else None,
            'initial_class': self.initial_class.to_dict(),
            'base_classes': [cls.to_dict() for cls in self.base_classes.all()],
            'base_lv': self.base_lv,
            'stats': {
                'hp': {
                    'base': self.base_hp,
                    'growth': self.growth_hp,
                    'max': self.max_hp,
                    'mod_max': self.max_hp,
                },
                'str': {
                    'base': self.base_str,
                    'growth': self.growth_str,
                    'max': self.max_str,
                    'mod_max': self.max_str,
                },
                'mag': {
                    'base': self.base_mag,
                    'growth': self.growth_mag,
                    'max': self.max_mag,
                    'mod_max': self.max_mag,
                },
                'skl': {
                    'base': self.base_skl,
                    'growth': self.growth_skl,
                    'max': self.max_skl,
                    'mod_max': self.max_skl,
                },
                'spd': {
                    'base': self.base_spd,
                    'growth': self.growth_spd,
                    'max': self.max_spd,
                    'mod_max': self.max_spd,
                },
                'luk': {
                    'base': self.base_luk,
                    'growth': self.growth_luk,
                    'max': self.max_luk,
                    'mod_max': self.max_luk,
                },
                'def': {
                    'base': self.base_def,
                    'growth': self.growth_def,
                    'max': self.max_def,
                    'mod_max': self.max_def,
                },
                'res': {
                    'base': self.base_res,
                    'growth': self.growth_res,
                    'max': self.max_res,
                    'mod_max': self.max_res,
                },
                'cha': {
                    'base': self.base_cha,
                    'growth': self.growth_cha,
                    'max': self.max_cha,
                    'mod_max': self.max_cha,
                },
                'mov': {
                    'base': self.base_mov,
                    'growth': self.growth_mov,
                    'max': self.max_mov,
                    'mod_max': self.max_mov,
                },
                'con': {
                    'base': self.base_con,
                    'growth': self.growth_con,
                    'max': self.max_con,
                    'mod_max': self.max_con,
                },
            },
            'ranks': {
                WeaponType.SWORD: self.base_rank_sword,
                WeaponType.LANCE: self.base_rank_lance,
                WeaponType.AXE: self.base_rank_axe,
                WeaponType.BOW: self.base_rank_bow,
                WeaponType.GAUNTLET: self.base_rank_gauntlet,
                WeaponType.HIDDEN: self.base_rank_hidden,
                WeaponType.TOME: self.base_rank_tome,
                WeaponType.FIRE: self.base_rank_fire,
                WeaponType.THUNDER: self.base_rank_thunder,
                WeaponType.WIND: self.base_rank_wind,
                WeaponType.DARK: self.base_rank_dark,
                WeaponType.LIGHT: self.base_rank_light,
                WeaponType.ANIMA: self.base_rank_anima,
                WeaponType.BLACK: self.base_rank_black,
                WeaponType.WHITE: self.base_rank_white,
                WeaponType.STAFF: self.base_rank_staff,
                WeaponType.DRAGONSTONE: self.base_rank_dragonstone,
                WeaponType.BEAST: self.base_rank_beast,
                WeaponType.SPECIAL: self.base_rank_special
            },
            'affinity': self.affinity,
            'bond_supports': [bs.to_dict() for bs in self.bond_supports.all()],
            'can_ranked_support': [u.id for u in self.can_ranked_support.all()],
            'personal_skills': [skl.to_dict() for skl in self.personal_skills.all()],
            'skill_tolerance': self.skill_tolerance
        }

    def __str__(self):
        return f"{self.game.abbrev}!{self.name} {f'- {self.route.name} route ' if self.route else ''}({self.id})"
