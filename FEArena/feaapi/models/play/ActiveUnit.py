from django.db import models
from .._util import BaseModel
from ..build.BuiltUnit import BuiltUnit
from .ActiveWeapon import ActiveWeapon
from .ActiveItem import ActiveItem
from ..core import Skill


class ActiveUnit(BaseModel):
    id: int = models.AutoField(primary_key=True)
    # demographic information should be contained in the template unit
    template: BuiltUnit = models.ForeignKey(BuiltUnit, on_delete=models.CASCADE)

    # for skill use. This should be reset at the beginning of each turn.
    restricted_actions: str = models.TextField(default='')

    # otherwise, current state information
    current_hp: int = models.IntegerField(default=0)
    mod_max_hp: int = models.IntegerField(default=0)
    mod_str: int = models.IntegerField(default=0)
    mod_mag: int = models.IntegerField(default=0, null=True, blank=True)
    mod_skl: int = models.IntegerField(default=0)
    mod_spd: int = models.IntegerField(default=0)
    mod_luk: int = models.IntegerField(default=0)
    mod_def: int = models.IntegerField(default=0)
    mod_res: int = models.IntegerField(default=0)
    mod_cha: int = models.IntegerField(default=0, null=True, blank=True)
    mod_mov: int = models.IntegerField(default=0)
    mod_con: int = models.IntegerField(default=0, null=True, blank=True)

    # inventory (limit should be in template unit)
    weapons = models.ManyToManyField(ActiveWeapon)
    items = models.ManyToManyField(ActiveItem)

    # weapon rank modifiers
    mod_rank_sword: int = models.IntegerField(default=0)
    mod_rank_lance: int = models.IntegerField(default=0)
    mod_rank_axe: int = models.IntegerField(default=0)
    mod_rank_bow: int = models.IntegerField(default=0)
    mod_rank_gauntlet: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_hidden: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_tome: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_fire: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_wind: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_thunder: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_dark: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_light: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_anima: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_black: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_white: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_staff: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_dragonstone: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_beast: int = models.IntegerField(default=0, null=True, blank=True)
    mod_rank_special: int = models.IntegerField(default=0, null=True, blank=True)

    # temporary skills
    temp_skills = models.ManyToManyField(Skill)

    def to_dict(self):
        # extract all_classes to its own variable at once, to keep the order consistent
        all_classes = self.template.unit_class_history.all()
        return {
            'id': self.id,
            'nickname': self.template.nickname,
            'name': self.template.unit.name,
            'description': self.template.unit.description,
            'sex': self.template.unit.sex,
            'game': self.template.unit.game.name,
            'route': self.template.unit.route.name if self.template.unit.route else None,
            'class': self.template.unit_class.to_dict(),
            'level': self.template.unit_level,
            'all_class_levels': [pc.levels for pc in all_classes],
            'current_hp': self.current_hp,
            'stats': {
                'level': self.template.unit_level,
                'hp': {
                    'unit_base': self.template.unit.base_hp,
                    'class_base': self.template.unit_class.base_hp,
                    'unit_growth': self.template.unit.growth_hp,
                    'all_class_growths': [pc.template.growth_hp for pc in all_classes],
                    'boosts': self.template.boosts_hp,
                    'modifiers': self.mod_max_hp,
                    'unit_max': self.template.unit.max_hp,
                    'unit_max_mod': self.template.unit.mod_max_hp,
                    'class_max': self.template.unit_class.max_hp
                },
                'str': {
                    'unit_base': self.template.unit.base_str,
                    'class_base': self.template.unit_class.base_str,
                    'unit_growth': self.template.unit.growth_str,
                    'all_class_growths': [pc.template.growth_str for pc in all_classes],
                    'boosts': self.template.boosts_str,
                    'modifiers': self.mod_str,
                    'unit_max': self.template.unit.max_str,
                    'unit_max_mod': self.template.unit.mod_max_str,
                    'class_max': self.template.unit_class.max_str
                },
                'mag': {
                    'unit_base': self.template.unit.base_mag,
                    'class_base': self.template.unit_class.base_mag,
                    'unit_growth': self.template.unit.growth_mag,
                    'all_class_growths': [pc.template.growth_mag for pc in all_classes],
                    'boosts': self.template.boosts_mag,
                    'modifiers': self.mod_mag,
                    'unit_max': self.template.unit.max_mag,
                    'unit_max_mod': self.template.unit.mod_max_mag,
                    'class_max': self.template.unit_class.max_mag
                },
                'skl': {
                    'unit_base': self.template.unit.base_skl,
                    'class_base': self.template.unit_class.base_skl,
                    'unit_growth': self.template.unit.growth_skl,
                    'all_class_growths': [pc.template.growth_skl for pc in all_classes],
                    'boosts': self.template.boosts_skl,
                    'modifiers': self.mod_skl,
                    'unit_max': self.template.unit.max_skl,
                    'unit_max_mod': self.template.unit.mod_max_skl,
                    'class_max': self.template.unit_class.max_skl
                },
                'spd': {
                    'unit_base': self.template.unit.base_spd,
                    'class_base': self.template.unit_class.base_spd,
                    'unit_growth': self.template.unit.growth_spd,
                    'all_class_growths': [pc.template.growth_spd for pc in all_classes],
                    'boosts': self.template.boosts_spd,
                    'modifiers': self.mod_spd,
                    'unit_max': self.template.unit.max_spd,
                    'unit_max_mod': self.template.unit.mod_max_spd,
                    'class_max': self.template.unit_class.max_spd
                },
                'luk': {
                    'unit_base': self.template.unit.base_luk,
                    'class_base': self.template.unit_class.base_luk,
                    'unit_growth': self.template.unit.growth_luk,
                    'all_class_growths': [pc.template.growth_luk for pc in all_classes],
                    'boosts': self.template.boosts_luk,
                    'modifiers': self.mod_luk,
                    'unit_max': self.template.unit.max_luk,
                    'unit_max_mod': self.template.unit.mod_max_luk,
                    'class_max': self.template.unit_class.max_luk
                },
                'def': {
                    'unit_base': self.template.unit.base_def,
                    'class_base': self.template.unit_class.base_def,
                    'unit_growth': self.template.unit.growth_def,
                    'all_class_growths': [pc.template.growth_def for pc in all_classes],
                    'boosts': self.template.boosts_def,
                    'modifiers': self.mod_def,
                    'unit_max': self.template.unit.max_def,
                    'unit_max_mod': self.template.unit.mod_max_def,
                    'class_max': self.template.unit_class.max_def
                },
                'res': {
                    'unit_base': self.template.unit.base_res,
                    'class_base': self.template.unit_class.base_res,
                    'unit_growth': self.template.unit.growth_res,
                    'all_class_growths': [pc.template.growth_res for pc in all_classes],
                    'boosts': self.template.boosts_res,
                    'modifiers': self.mod_res,
                    'unit_max': self.template.unit.max_res,
                    'unit_max_mod': self.template.unit.mod_max_res,
                    'class_max': self.template.unit_class.max_res
                },
                'cha': {
                    'unit_base': self.template.unit.base_cha,
                    'class_base': self.template.unit_class.base_cha,
                    'unit_growth': self.template.unit.growth_cha,
                    'all_class_growths': [pc.template.growth_cha for pc in all_classes],
                    'boosts': self.template.boosts_cha,
                    'modifiers': self.mod_cha,
                    'unit_max': self.template.unit.max_cha,
                    'unit_max_mod': self.template.unit.mod_max_cha,
                    'class_max': self.template.unit_class.max_cha
                },
                'con': {
                    'unit_base': self.template.unit.base_con,
                    'class_base': self.template.unit_class.base_con,
                    'unit_growth': self.template.unit.growth_con,
                    'all_class_growths': [pc.template.growth_con for pc in all_classes],
                    'boosts': self.template.boosts_con,
                    'modifiers': self.mod_con,
                    'unit_max': self.template.unit.max_con,
                    'unit_max_mod': self.template.unit.mod_max_con,
                    'class_max': self.template.unit_class.max_con
                },
                'mov': {
                    'unit_base': self.template.unit.base_mov,
                    'class_base': self.template.unit_class.base_mov,
                    'unit_growth': self.template.unit.growth_mov,
                    'all_class_growths': [pc.template.growth_mov for pc in all_classes],
                    'boosts': self.template.boosts_mov,
                    'modifiers': self.mod_mov,
                    'unit_max': self.template.unit.max_mov,
                    'unit_max_mod': self.template.unit.mod_max_mov,
                    'class_max': self.template.unit_class.max_mov
                },
            },
            'weapon_ranks': {
                'sword': {
                    'unit_base': self.template.unit.base_rank_sword,
                    'class_base': self.template.unit_class.base_rank_sword,
                    'boosts': self.template.boost_rank_sword,
                    'modifiers': self.mod_rank_sword,
                },
                'lance': {
                    'unit_base': self.template.unit.base_rank_lance,
                    'class_base': self.template.unit_class.base_rank_lance,
                    'boosts': self.template.boost_rank_lance,
                    'modifiers': self.mod_rank_lance,
                },
                'axe': {
                    'unit_base': self.template.unit.base_rank_axe,
                    'class_base': self.template.unit_class.base_rank_axe,
                    'boosts': self.template.boost_rank_axe,
                    'modifiers': self.mod_rank_axe,
                },
                'bow': {
                    'unit_base': self.template.unit.base_rank_bow,
                    'class_base': self.template.unit_class.base_rank_bow,
                    'boosts': self.template.boost_rank_bow,
                    'modifiers': self.mod_rank_bow,
                },
                'gauntlet': {
                    'unit_base': self.template.unit.base_rank_gauntlet,
                    'class_base': self.template.unit_class.base_rank_gauntlet,
                    'boosts': self.template.boost_rank_gauntlet,
                    'modifiers': self.mod_rank_gauntlet,
                },
                'hidden': {
                    'unit_base': self.template.unit.base_rank_hidden,
                    'class_base': self.template.unit_class.base_rank_hidden,
                    'boosts': self.template.boost_rank_hidden,
                    'modifiers': self.mod_rank_hidden,
                },
                'tome': {
                    'unit_base': self.template.unit.base_rank_tome,
                    'class_base': self.template.unit_class.base_rank_tome,
                    'boosts': self.template.boost_rank_tome,
                    'modifiers': self.mod_rank_tome,
                },
                'fire': {
                    'unit_base': self.template.unit.base_rank_fire,
                    'class_base': self.template.unit_class.base_rank_fire,
                    'boosts': self.template.boost_rank_fire,
                    'modifiers': self.mod_rank_fire,
                },
                'wind': {
                    'unit_base': self.template.unit.base_rank_wind,
                    'class_base': self.template.unit_class.base_rank_wind,
                    'boosts': self.template.boost_rank_wind,
                    'modifiers': self.mod_rank_wind,
                },
                'thunder': {
                    'unit_base': self.template.unit.base_rank_thunder,
                    'class_base': self.template.unit_class.base_rank_thunder,
                    'boosts': self.template.boost_rank_thunder,
                    'modifiers': self.mod_rank_thunder,
                },
                'dark': {
                    'unit_base': self.template.unit.base_rank_dark,
                    'class_base': self.template.unit_class.base_rank_dark,
                    'boosts': self.template.boost_rank_dark,
                    'modifiers': self.mod_rank_dark,
                },
                'light': {
                    'unit_base': self.template.unit.base_rank_light,
                    'class_base': self.template.unit_class.base_rank_light,
                    'boosts': self.template.boost_rank_light,
                    'modifiers': self.mod_rank_light,
                },
                'anima': {
                    'unit_base': self.template.unit.base_rank_anima,
                    'class_base': self.template.unit_class.base_rank_anima,
                    'boosts': self.template.boost_rank_anima,
                    'modifiers': self.mod_rank_anima,
                },
                'black': {
                    'unit_base': self.template.unit.base_rank_black,
                    'class_base': self.template.unit_class.base_rank_black,
                    'boosts': self.template.boost_rank_black,
                    'modifiers': self.mod_rank_black,
                },
                'white': {
                    'unit_base': self.template.unit.base_rank_white,
                    'class_base': self.template.unit_class.base_rank_white,
                    'boosts': self.template.boost_rank_white,
                    'modifiers': self.mod_rank_white,
                },
                'staff': {
                    'unit_base': self.template.unit.base_rank_staff,
                    'class_base': self.template.unit_class.base_rank_staff,
                    'boosts': self.template.boost_rank_staff,
                    'modifiers': self.mod_rank_staff,
                },
                'dragonstone': {
                    'unit_base': self.template.unit.base_rank_dragonstone,
                    'class_base': self.template.unit_class.base_rank_dragonstone,
                    'boosts': self.template.boost_rank_dragonstone,
                    'modifiers': self.mod_rank_dragonstone,
                },
                'beast': {
                    'unit_base': self.template.unit.base_rank_beast,
                    'class_base': self.template.unit_class.base_rank_beast,
                    'boosts': self.template.boost_rank_beast,
                    'modifiers': self.mod_rank_beast,
                },
                'special': {
                    'unit_base': self.template.unit.base_rank_special,
                    'class_base': self.template.unit_class.base_rank_special,
                    'boosts': self.template.boost_rank_special,
                    'modifiers': self.mod_rank_special,
                },
            },
            'inventory': {
                'weapons': [weapon.to_dict() for weapon in self.weapons.all()],
                'items': [item.to_dict() for item in self.items.all()],
            },
            'personal_skills': [skill.to_dict() for skill in self.template.unit.personal_skills.all()],
            'extra_skills': [skill.to_dict() for skill in self.template.extra_skills.all()],
            'temporary_skills': [skill.to_dict() for skill in self.temp_skills.all()]
        }
