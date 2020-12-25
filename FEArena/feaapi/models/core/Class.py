from django.db import models
from .._util import BaseModel, maxlength
from .Skill import Skill
from .Game import FireEmblemGame
from .WeaponType import WeaponType
from .WeaponRank import WeaponRank


_wrml = maxlength(WeaponRank)


class Class(BaseModel):
    # core class info
    id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(max_length=255)
    name_detail: str = models.CharField(max_length=255)  # e.g. Hero (F) rather than just Hero
    description: str = models.CharField(max_length=255)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    promotes_to = models.ManyToManyField('self')
    minimum_promotion_level: int = models.IntegerField(default=10, null=True, blank=True)
    maximum_level: int = models.IntegerField(default=20)

    # EXP/Point calculation factors (used differently depending on the game's mechanics)
    # - FE1, FE3, and FE4 do not use class EXP or class strength in their EXP formulae
    # - FE2: Class EXP is unused, but Class Strength is
    #       1:  Gold Knight • Baron • Bow Knight • Falcon Knight • Necrodragon • White Dragon • Fiend • Hades • Aurum
    #       2:  Dread Fighter • Sage • Cantor • Kelbeth • Naberius
    #       3:  Paladin
    #       4:  Myrmidon • Sniper
    #       5:  Knight • Mage (Male units) • Priestess • Princess • Fighter • Hero • Arcanist • Revenant • Entombed •
    #           Fell God
    #       6:  Cavalier • Pegasus Knight • Mage (Female units) • Witch • Gargoyle • Deathgoyle • Arcanist
    #       7:  Mercenary • Archer • Saint • Bonewalker • Lich
    #       8:  Soldier
    #       10: Villager • Brigand • Cleric • Mogall
    # - FE15: uses the same EXP formula as Gaiden, but with the following differnet class strengths:
    #       1:  Gold Knight • Baron • Bow Knight • Falcon Knight • Priestess (normal version) • Necrodragon •
    #           White Dragon • Fiend • Guardian • Vestal • Fafnir • Dagon • Balor • Deimos • Fire Dragon •
    #           Fell Dragon • Skogul • Spartan • Oliphantier • Harrier • Enchantress • Tomb Lord • Mila's Servant •
    #           Duma's Apostle
    #       2:  Dread Fighter • Sage • Saint • Princess • Hero • Cantor • Lich • Deathgoyle • Titan • Garuda • Yasha •
    #           Guru • Exemplar • Rigain • Conqueror • Illusory Hero
    #       3:  Paladin • Mogall
    #       4:  Myrmidon • Sniper • Dracul
    #       5:  Knight • Mage (Male units) • Priestess (Celica version) • Fighter • Arcanist • Revenant • Entombed •
    #           Fell God
    #       6:  Cavalier • Pegasus Knight • Mage (Female units) • Witch • Gargoyle • Arcanist
    #       7:  Mercenary • Archer • Bonewalker
    #       8:  Soldier • Cleric
    #       10: Villager • Boy • Girl • Brigand
    # - FE5: Class EXP is unused. Note that a unit gets bonus EXP if their opponent has the Steal skill, which
    #       should be treated as an after_combat effect of the Steal skill. Class Strength is
    #       1: Priest, Sister
    #       2: Troubadour, Bow Fighter, Mountain Thief (2), Hunter, Pirate, Dancer, High Priest, Bishop, Thief,
    #          Soldier, Archer
    #       3: Everything not listed
    #       4: Duke Knight, Paladin (M), Bow Knight, Forrest Knight, Mage Knight (M), Great Knight, Pegasus Knight,
    #          Dragon Knight, Sniper, General, Warrior, Prince, Dark Bishop, Killer Arch, Mercenary
    #       5: Swordmaster, Baron, Berserker, Sage, Iron Arch
    # - GBA: Class EXP and Class Strength are used explicitly. Class EXP:
    #       - Class Strength:
    #           1:  Bramimond, Child, Civilian, Journeyman (1), Peer, Pontifex, Prince, Princess, Pupil (1), Queen,
    #               Recruit (1), Transporter
    #           2:  Bard, Cleric, Dancer, Divine Dragon (unused), Manakete (female), Priest, Soldier, Troubadour, Thief
    #           3:  Lord, Knight Lord, Blade Lord, Great Lord, Cavalier, Paladin, Great Knight, Pegasus Knight,
    #               Falcoknight, Wyvern Rider, Wyvern Lord, Wyvern Knight, Nomad, Nomad Trooper, Ranger, Mage Knight,
    #               Valkyrie, Myrmidon, Swordmaster, Mercenary, Hero, Knight, General, Fighter, Warrior, Pirate,
    #               Brigand, Berserker, Archer, Sniper, Mage, Sage, Monk, Bishop, Shaman, Druid, Summoner, Dark Druid,
    #               Necromancer, Rogue, Assassin, Manakete (male), Magic Seal, Archsage, Journeyman (2 and 3),
    #               Pupil (2 and 3), Recruit (2 and 3), Bonewalker, Wight, Gargoyle, Deathgoyle, Tarvos, Maelduin,
    #               Cyclops, Fleet, Mogall, Arch Mogall, Gorgon, Entombed, Revenant, Mauthe Doog, Gwyllgi, Bael,
    #               Elder Bael, Draco Zombie
    #           4:  Paladin (female; The Binding Blade only)
    #           5:  Fire Dragon, King, Demon Dragon, Demon King
    #       - Class EXP for both player and enemy units is 40 if the unit is a Bishop (female only in FE7),
    #           Valkyrie, Rogue, or Assassin; 60 if the unit is any other promoted class; 0 otherwise.
    #       - There's supposed to be an additional bonus of 20exp if opponent is a Thief, Rogue, or Assassin,
    #           or 40exp if opponent is an Entombed. Factor this into class bonus, maybe. I'm not sure it's
    #           accounted for in the link arena
    #       - The Silencer skill triggering adds additional EXP equal to enemy's level * class strength.
    # - FE9: does not use class_exp or class_strength
    # - FE10: Special point about FE10: Laguz are special. They shall have a class_exp of 2, everything else
    #       shall have a class_exp of 1, and this shall be used as a multiplier in the formula, to simulate
    #       their level being doubled. This is much different from the normal base class_exp values.
    #       Additionally, since RD has three-tier promotions, the difference between tier2 and tier3 will be
    #       whether the class's promotes_to has any items in it.
    # - FE11: Class EXP for Thieves is 20, everything else should be 0
    # - FE12: Class EXP for Thieves, Emperors, Ballisticians is 20;
    #       Class Strength should be 3 for non-manaketes and 5 for manaketes
    # - FE13: Class EXP is 20 for Thief, Assassin, Trickster, Conqueror; 80 for Revenant/Entombed;
    #       -10 for Troubador, Cleric, Priest; 0 otherwise. Class Strength is unused
    # - FE16: uses Class EXP but not Class Strength. Class EXP presumably corresponds to class tier, which is
    #       in some database somewhere, but I don't know it as of writing this comment
    class_exp: int = models.IntegerField(default=0)  # For EXP calculations
    class_strength: int = models.IntegerField(default=3)
    promoted: bool = models.BooleanField(default=True)  # for EXP calculations only

    # class base stats
    base_hp: int = models.IntegerField(default=0)
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

    # class growths
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

    # class max stats
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

    # demographics / damage types
    cavalry: bool = models.BooleanField(default=False)
    flying: bool = models.BooleanField(default=False)
    armored: bool = models.BooleanField(default=False)
    wyvern: bool = models.BooleanField(default=False)
    dragon: bool = models.BooleanField(default=False)
    undead: bool = models.BooleanField(default=False)
    infantry: bool = models.BooleanField(default=True)

    # movement costs
    movement_cost_floor: float = models.FloatField(default=1)
    movement_cost_forest: float = models.FloatField(default=2)
    movement_cost_thicket: float = models.FloatField(default=-1)
    movement_cost_mountain: float = models.FloatField(default=4)
    movement_cost_peak: float = models.FloatField(default=-1)
    movement_cost_cliff: float = models.FloatField(default=-1)
    movement_cost_sand: float = models.FloatField(default=1)
    movement_cost_desert: float = models.FloatField(default=2)
    movement_cost_pillar: float = models.FloatField(default=2)
    movement_cost_wall: float = models.FloatField(default=-1)
    movement_cost_fort: float = models.FloatField(default=2)
    movement_cost_gate: float = models.FloatField(default=1)
    movement_cost_throne: float = models.FloatField(default=1)
    movement_cost_grave: float = models.FloatField(default=1)
    movement_cost_ruins: float = models.FloatField(default=2)
    movement_cost_river: float = models.FloatField(default=5)
    movement_cost_sea: float = models.FloatField(default=-1)
    movement_cost_lake: float = models.FloatField(default=-1)
    movement_cost_road: float = models.FloatField(default=0.7)
    movement_cost_building: float = models.FloatField(default=1)
    movement_cost_aerial: float = models.FloatField(default=-1)
    movement_cost_wasteland: float = models.FloatField(default=1)

    # class weapon types (doubles as "can use this weapon" if base rank is E or higher
    # records number of points, not actual weapon rank
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

    max_rank_sword: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_lance: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_axe: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_bow: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_gauntlet: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_hidden: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_tome: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_fire: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_thunder: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_wind: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_dark: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_light: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_anima: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_black: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_white: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_staff: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_dragonstone: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_beast: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)
    max_rank_special: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.NONE, max_length=_wrml)

    # other data
    class_skills = models.ManyToManyField(Skill)

    def to_dict(self):
        """
        :return: a JSON-compatible representation of this class, conforming to the appropriate
            JSON schema in api.teambuilder.schema
        """
        return {
            'id': self.id,
            'name': self.name,
            'detail': self.name_detail,
            'description': self.description,
            'game': self.game.abbrev,
            'promotes_to': [cls.id for cls in self.promotes_to.all()],
            'promotion_level': self.minimum_promotion_level,
            'max_level': self.maximum_level,
            'class_strength': self.class_strength,
            'class_exp': self.class_exp,
            'promoted': self.promoted,
            'damage_types': {
                'cavalry': self.cavalry,
                'flying': self.flying,
                'armored': self.armored,
                'wyvern': self.wyvern,
                'dragon': self.dragon,
                'infantry': self.infantry,
            },
            'movement_costs': {
                'floor': self.movement_cost_floor,
                'forest': self.movement_cost_forest,
                'thicket': self.movement_cost_thicket,
                'mountain': self.movement_cost_mountain,
                'peak': self.movement_cost_peak,
                'cliff': self.movement_cost_cliff,
                'sand': self.movement_cost_sand,
                'desert': self.movement_cost_desert,
                'pillar': self.movement_cost_pillar,
                'wall': self.movement_cost_wall,
                'fort': self.movement_cost_fort,
                'gate': self.movement_cost_gate,
                'throne': self.movement_cost_throne,
                'grave': self.movement_cost_grave,
                'river': self.movement_cost_river,
                'sea': self.movement_cost_sea,
                'road': self.movement_cost_road,
                'building': self.movement_cost_building,
                'aerial': self.movement_cost_aerial,
                'wasteland': self.movement_cost_wasteland,
            },
            'stats': {
                'hp': {
                    'base': self.base_hp,
                    'max': self.max_hp,
                    'growth': self.growth_hp,
                },
                'str': {
                    'base': self.base_str,
                    'max': self.max_str,
                    'growth': self.growth_str,
                },
                'mag': {
                    'base': self.base_mag,
                    'max': self.max_mag,
                    'growth': self.growth_mag,
                },
                'skl': {
                    'base': self.base_skl,
                    'max': self.max_skl,
                    'growth': self.growth_skl,
                },
                'spd': {
                    'base': self.base_spd,
                    'max': self.max_spd,
                    'growth': self.growth_spd,
                },
                'luk': {
                    'base': self.base_luk,
                    'max': self.max_luk,
                    'growth': self.growth_luk,
                },
                'def': {
                    'base': self.base_def,
                    'max': self.max_def,
                    'growth': self.growth_def,
                },
                'res': {
                    'base': self.base_res,
                    'max': self.max_res,
                    'growth': self.growth_res,
                },
                'cha': {
                    'base': self.base_cha,
                    'max': self.max_cha,
                    'growth': self.growth_cha,
                },
                'mov': {
                    'base': self.base_mov,
                    'max': self.max_mov,
                    'growth': self.growth_mov,
                },
                'con': {
                    'base': self.base_con,
                    'max': self.max_con,
                    'growth': self.growth_con,
                },
            },
            'ranks': {
                WeaponType.SWORD: {
                    'base': self.base_rank_sword,
                    'max': self.max_rank_sword
                },
                WeaponType.LANCE: {
                    'base': self.base_rank_lance,
                    'max': self.max_rank_lance
                },
                WeaponType.AXE: {
                    'base': self.base_rank_axe,
                    'max': self.max_rank_axe
                },
                WeaponType.BOW: {
                    'base': self.base_rank_bow,
                    'max': self.max_rank_bow
                },
                WeaponType.GAUNTLET: {
                    'base': self.base_rank_gauntlet,
                    'max': self.max_rank_gauntlet
                },
                WeaponType.HIDDEN: {
                    'base': self.base_rank_hidden,
                    'max': self.max_rank_hidden
                },
                WeaponType.TOME: {
                    'base': self.base_rank_tome,
                    'max': self.max_rank_tome
                },
                WeaponType.FIRE: {
                    'base': self.base_rank_fire,
                    'max': self.max_rank_fire
                },
                WeaponType.THUNDER: {
                    'base': self.base_rank_thunder,
                    'max': self.max_rank_thunder
                },
                WeaponType.WIND: {
                    'base': self.base_rank_wind,
                    'max': self.max_rank_wind
                },
                WeaponType.DARK: {
                    'base': self.base_rank_dark,
                    'max': self.max_rank_dark
                },
                WeaponType.LIGHT: {
                    'base': self.base_rank_light,
                    'max': self.max_rank_light
                },
                WeaponType.ANIMA: {
                    'base': self.base_rank_anima,
                    'max': self.max_rank_anima
                },
                WeaponType.BLACK: {
                    'base': self.base_rank_black,
                    'max': self.max_rank_black
                },
                WeaponType.WHITE: {
                    'base': self.base_rank_white,
                    'max': self.max_rank_white
                },
                WeaponType.STAFF: {
                    'base': self.base_rank_staff,
                    'max': self.max_rank_staff
                },
                WeaponType.DRAGONSTONE: {
                    'base': self.base_rank_dragonstone,
                    'max': self.max_rank_dragonstone
                },
                WeaponType.BEAST: {
                    'base': self.base_rank_beast,
                    'max': self.max_rank_beast
                },
                WeaponType.SPECIAL: {
                    'base': self.base_rank_special,
                    'max': self.max_rank_special
                },
            },
            'skills': [skill.to_dict() for skill in self.class_skills.all()]
        }

    def __str__(self):
        return f"{self.game.abbrev}!{self.name_detail} ({self.id})"
