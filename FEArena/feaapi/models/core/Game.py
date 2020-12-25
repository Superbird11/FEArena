from django.db import models
from .._util import BaseModel, maxlength


class WeaponRank(models.TextChoices):
    SS = 'SS'
    S = 'S'
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    PRF = 'Prf'
    NONE = '--'


class WeaponBreakBehavior(models.TextChoices):
    BREAK = 'B'
    REMOVE = 'R'


class AttackSpeedCalculationMethod(models.TextChoices):
    SPEED = 'Spd'  # FE11 - FE14
    SPEED_MINUS_WEIGHT = 'Spd-Wt'  # FE1 - FE4, FE15
    SPEED_MINUS_WEIGHT_MINUS_CON_BUT_NOT_FOR_MAGIC = 'Spd-(Wt-Con);Spd-Wt'
    SPEED_MINUS_WEIGHT_MINUS_CON = 'Spd-(Wt-Con)'  # FE6 - FE8
    SPEED_MINUS_WEIGHT_MINUS_STR = 'Spd-(Wt-Str)'  # FE9 - FE10
    SPEED_MINUS_WEIGHT_MINUS_STR_OVER_FIVE = 'Spd-(Wt-Str/5)'  # FE16


class HitCalculationMethod(models.TextChoices):
    SKL_NOT_MAGIC = 'Skl+Hit;Hit'  # FE1 - FE2
    SKL_TIMES_2 = 'Skl*2+Hit'  # FE3 - FE4
    SKL_TIMES_2_PLUS_LUK = 'Skl*2+Hit+Luk'  # FE5, FE10
    SKL_TIMES_2_PLUS_HALF_LUK = 'Skl*2+Hit+Luk/2'  # FE6, FE9
    SKL_TIMES_2_PLUS_HALF_LUK_PLUS_RANK = 'Skl*2+Hit+Luk/2+Rank'  # FE7 - FE8
    SKL_PLUS_HALF_LUK_PLUS_RANK = 'Skl+Hit+Luk/2+Rank'  # FE11 - FE12
    SKL_TIMES_THREEHALFS_PLUS_HALF_LUK_PLUS_RANK = 'Skl*1.5+Hit+Luk/2+Rank'  # FE13 - FE14
    SKL_OR_HALF_SKL_PLUS_LUK = 'Skl+Hit;(Skl+Luk)/2+Hit'  # FE15 - FE16


class StaffHitCalculationMethod(models.TextChoices):
    ALWAYS = 'Always'  # other FE games, assumed
    MAG_PLUS_SKL_PLUS_HIT_PLUS_RANK = 'Mag+Skl+Hit+Rank'  # FE14
    MAG_TIMES_5_PLUS_SKILL_PLUS_30 = 'Mag*5+Skl+30'  # FE7-8
    MAG_MINUS_RES_TIMES_6_PLUS_SKL_PLUS_30_MINUS_DISTANCE = '(Mag-Res)*6+Skl+30-Dist'  # FE6
    SKL_TIMES_4_PLUS_HIT = 'Skl*4+Hit'  # FE5
    MAG_EXCEEDS_RES = 'Mag>Res'  # FE4


class AvoidCalculationMethod(models.TextChoices):  # this does not factor in terrain, which happens later
    AS_OR_LUK = 'AS;Luk'  # FE1 - for physical, AS, for magical, Luk
    AS_OR_SPD_PLUS_LUK = 'AS;Spd+Luk'  # FE2
    SPD_PLUS_LUK = 'Spd+Luk'  # FE3
    AS_TIMES_TWO_PLUS_LUK = 'AS*2+Luk'  # FE4 - FE10
    AS_PLUS_HALF_LUCK = 'AS+Luk/2'  # FE11 - FE12
    AS_TIMES_THREEHALFS_PLUS_HALF_LUK = 'AS*1.5+Luk/2'  # FE13 - FE14
    AS_OR_HALF_SPD_PLUS_LUK = 'AS;(Spd+Luk)/2'  # FE15 - FE16


class CritRateCalculationMethod(models.TextChoices):
    HALF_SKILL_PLUS_LUK = 'Crit+(Skl+Luk)/2'  # FE1 - FE2, FE15 - FE16
    SKL = 'Crit+Skl'  # FE3, FE5
    ZERO = '0'  # FE4 - skills, weapon kill bonuses, and combo attacks compensate for this, but those are separate
    HALF_SKILL = 'Crit+Skl/2'  # FE6, FE9 - FE11, FE13
    HALF_SKILL_PLUS_RANK = 'Crit+Skl/2+Rank'  # FE7 - FE8 have crit bonuses at S-rank
    HALF_SKILL_OR_SKILL_MINUS_10 = 'Crit+max(Skl/2,Skl-10)'  # FE12
    HALF_SKILL_MINUS_FOUR = 'Crit+(Skl-4)/2'  # FE14


class CritAvoidCalculationMethod(models.TextChoices):
    ZERO = '0'  # FE1, FE2, FE4
    LUK = 'Luk'  # Most FE games
    HALF_LUK = 'Luk/2'  # FE3, FE14, FE15


class AttackCalculationMethod(models.TextChoices):  # does not include weapon effectiveness
    NO_WEAPON_TRIANGLE = 'Str+Mt'  # FE1 - FE5, FE15, FE16
    WEAPON_TRIANGLE = 'Str+Mt+WT'  # FE6 - FE10
    WEAPON_TRIANGLE_RANK = 'Str+Mt+WT+Rank'  # FE11 - FE14


class WeaponTriangleType(models.TextChoices):
    NONE = 'None'  # FE1 - FE3, FE15, FE16
    PHYSICAL = 'Sword<Lance<Axe'  # FE11 - 13
    MAGIC_ANIMA_SINGLE = '(Fire<Thunder<Wind)<(Light=Dark)'  # FE4, FE5
    MAGIC_TRINITY_SINGLE = 'Anima<Light<Dark'  # FE6 - FE8
    MAGIC_DOUBLE = '(Fire<Thunder<Wind)<Light<Dark'  # FE9 - FE10
    ALL = 'Sword/Magic<Lance/Hidden<Axe/Bow'  # FE14


class AttackEffectiveDamageCalculationMethod(models.TextChoices):
    NO_EFFECTIVE = 'None'  # FE4
    MT_EFFECTIVE = 'Mt'  # FE1, FE3, FE5, FE11 - FE14
    DMG_EFFECTIVE = 'Str+Mt'  # FE2, FE15
    MT_WT_EFFECTIVE = 'Mt+WT'  # FE6 - FE10


class AttackEffectiveDamageModifier(models.IntegerChoices):
    NONE = 1
    DOUBLE = 2
    TRIPLE = 3
    SKILL_DEPENDENT = 0


class FollowUpCriteria(models.IntegerChoices):
    SKILL_ONLY = 0  # follow-up is tied to having a skill, which executes the attack itself
    HIGHER_AS = 1  # follow-up if unit's AS exceeds opponent's by 1 point
    THREE_HIGHER_AS = 3  # follow-up if unit's AS exceeds opponent's by 3 points
    FOUR_HIGHER_AS = 4  # follow-up if unit's AS exceeds opponent's by 4 points
    FIVE_HIGHER_AS = 5  # follow-up if unit's AS exceeds opponent's by 5 points


class CritDamageCalculationMethod(models.TextChoices):
    ATK_TIMES_2 = 'ATK*2'  # crits double ATK before DMG is calculated
    DMG_TIMES_3 = 'DMG*3'  # crits deal 3 * DMG


class HitRNGMethod(models.TextChoices):
    ONE_RN = '1RN'  # FE1 - FE5
    TWO_RN = '2RN'  # FE6 - FE13, FE16
    HYBRID = 'Hybrid'  # FE14 - FE15


class EXPFormula(models.TextChoices):
    FE1 = 'FE1'  # FE1
    FE2 = 'FE2'  # FE2, also FE15 I think
    FE3 = 'FE3'  # FE3
    FE4 = 'FE4'  # FE4
    FE5 = 'FE5'  # FE5
    GBA_HARD = 'FE6'  # FE6; division factor is always 1
    GBA_EASY = 'FE7-FE8'  # FE7-8 easy modes/earlygame, respectively; division factor can be 2, depending.
    FE9 = 'FE9 (Normal)'  # FE9
    FE9_EASY = 'FE9 (Easy)'
    FE9_HARD = 'FE9 (Hard)'
    FE9_MANIAC = 'FE9 (Maniac)'
    FE10 = 'FE10 (Normal)'  # FE10
    FE10_HARD = 'FE10 (Hard)'
    FE11 = 'FE11'  # FE11
    FE12 = 'FE12'  # FE12
    FE13 = 'FE13'  # FE13 (omitting the Lunatic EXP Factor)
    # TODO figure out FE14 exp mechanics
    FE16 = 'FE16 (Normal)'  # FE16
    FE16_HARD = 'FE16 (Hard)'
    FE16_MADDENING = 'FE16 (Maddening)'


class ChangeClassBehavior(models.TextChoices):
    RESET_LEVEL = 'RESET',
    KEEP_LEVEL = 'KEEP'


class ClassChangeEligibility(models.TextChoices):
    NO = 'No'  # Most games, where reclassing is not allowed
    ABLE_TO_PROMOTE = 'FE13'  # after level 10 of a class that can promote, or anytime in a promoted class
    ANYTIME = 'Yes'  # FE11-12, FE14
    MINIMUM_PROMOTION_LEVEL = 'FE16'  # If unit level exceeds Minimum Promotion Level of new class


class SkillLimit(models.TextChoices):
    NONE = 'None'
    QUANTITY = 'Quantity'
    UNIT_TOLERANCE = 'Tolerance'


class PromotionBonus(models.TextChoices):
    SEPARATE = 'Separate'  # There's a separate table of promotion bonuses for each change
    BASES = 'Bases'  # The unit's stats change in accordance to the classes' base stats


class SupportRank(models.IntegerChoices):
    NONE = 0
    C = 1
    B = 2
    A = 3
    S = 4


class BondSupportBehavior(models.TextChoices):
    NONE = 'None'
    HIT_AVO_CRIT = 'FE3'  # boosts Hit, Avo, and Crit by the strength of the bond support
    HIT_AVO_CRIT_DDG = 'FE5'  # boosts Hit, Avo, Crit, and Ddg by the strength of the bond support
    UNIT_SPECIFIC = 'FE15'
    FE16_FLAT = 'FE16'  # boosts by a specific flat rate that doesn't map to a linear formula


class RankedSupportBehavior(models.TextChoices):
    NONE = 'None'
    GBA_AFFINITY = 'GBA'
    FE9_AFFINITY = 'FE9'
    FE10_AFFINITY = 'FE10'
    DS_FLAT = 'DS'
    DUALSTRIKE_PAIRUP = 'FE13'  # this is very complicated
    TAGTEAM_PAIRUP = 'FE14'  # this is hellishly complicated
    FE15_UNIT_SPECIFIC = 'FE15'
    FE16_FLAT = 'FE16'


class AffinityTypes(models.TextChoices):
    NONE = 'None',
    GBA = 'GBA',
    TELLIUS = 'Tellius'


class FireEmblemGame(BaseModel):
    abbrev: str = models.CharField(primary_key=True, max_length=16)
    name: str = models.CharField(max_length=255)
    index: int = models.IntegerField(blank=True, null=True)
    on_weapon_break: str = models.CharField(choices=WeaponBreakBehavior.choices, default=WeaponBreakBehavior.REMOVE,
                                            max_length=maxlength(WeaponBreakBehavior))
    attack_speed_method: str = models.CharField(choices=AttackSpeedCalculationMethod.choices,
                                                default=AttackSpeedCalculationMethod.SPEED_MINUS_WEIGHT_MINUS_CON,
                                                max_length=maxlength(AttackSpeedCalculationMethod))
    follow_up_criteria: int = models.IntegerField(choices=FollowUpCriteria.choices,
                                                  default=FollowUpCriteria.FOUR_HIGHER_AS)
    crit_damage: str = models.CharField(choices=CritDamageCalculationMethod.choices,
                                        default=CritDamageCalculationMethod.DMG_TIMES_3,
                                        max_length=maxlength(CritDamageCalculationMethod))
    hit_method: str = models.CharField(choices=HitCalculationMethod.choices,
                                       default=HitCalculationMethod.SKL_TIMES_2_PLUS_HALF_LUK_PLUS_RANK,
                                       max_length=maxlength(HitCalculationMethod))
    staff_hit_method: str = models.CharField(choices=StaffHitCalculationMethod.choices,
                                             default=StaffHitCalculationMethod.MAG_TIMES_5_PLUS_SKILL_PLUS_30,
                                             max_length=maxlength(StaffHitCalculationMethod))
    avoid_method: str = models.CharField(choices=AvoidCalculationMethod.choices,
                                         default=AvoidCalculationMethod.AS_TIMES_TWO_PLUS_LUK,
                                         max_length=maxlength(AvoidCalculationMethod))
    crit_method: str = models.CharField(choices=CritRateCalculationMethod.choices,
                                        default=CritRateCalculationMethod.HALF_SKILL_PLUS_RANK,
                                        max_length=maxlength(CritRateCalculationMethod))
    crit_avoid_method: str = models.CharField(choices=CritAvoidCalculationMethod.choices,
                                              default=CritAvoidCalculationMethod.LUK,
                                              max_length=maxlength(CritAvoidCalculationMethod))
    attack_method: str = models.CharField(choices=AttackCalculationMethod.choices,
                                          default=AttackCalculationMethod.WEAPON_TRIANGLE,
                                          max_length=maxlength(AttackCalculationMethod))
    weapon_triangle: str = models.CharField(choices=WeaponTriangleType.choices,
                                            default=WeaponTriangleType.MAGIC_ANIMA_SINGLE,
                                            max_length=maxlength(WeaponTriangleType))
    attack_effective_method: str = models.CharField(choices=AttackEffectiveDamageCalculationMethod.choices,
                                                    default=AttackEffectiveDamageCalculationMethod.MT_WT_EFFECTIVE,
                                                    max_length=maxlength(AttackEffectiveDamageCalculationMethod))
    attack_effective_mod: int = models.IntegerField(choices=AttackEffectiveDamageModifier.choices,
                                                    default=AttackEffectiveDamageModifier.TRIPLE)
    class_change_behavior: str = models.CharField(choices=ChangeClassBehavior.choices,
                                                  default=ChangeClassBehavior.KEEP_LEVEL,
                                                  max_length=maxlength(ChangeClassBehavior))
    promotion_behavior: str = models.CharField(choices=ChangeClassBehavior.choices,
                                               default=ChangeClassBehavior.RESET_LEVEL,
                                               max_length=maxlength(ChangeClassBehavior))
    promotion_bonuses: str = models.CharField(choices=PromotionBonus.choices, default=PromotionBonus.SEPARATE,
                                              max_length=maxlength(PromotionBonus))
    max_weapon_rank: str = models.CharField(choices=WeaponRank.choices, default=WeaponRank.S,
                                            max_length=maxlength(WeaponRank))
    mutually_exclusive_max_weapon_rank: bool = models.BooleanField(default=True)
    class_change_allowed: str = models.CharField(choices=ClassChangeEligibility.choices,
                                                 default=ClassChangeEligibility.NO,
                                                 max_length=maxlength(ClassChangeEligibility))
    exp_method: str = models.CharField(choices=EXPFormula.choices, default=EXPFormula.GBA_EASY,
                                       max_length=maxlength(EXPFormula))
    rng_method: str = models.CharField(choices=HitRNGMethod.choices, default=HitRNGMethod.TWO_RN,
                                       max_length=maxlength(HitRNGMethod))
    magic_ignores_terrain: bool = models.BooleanField(default=False)
    has_mag_stat: bool = models.BooleanField(default=True)
    weapon_triangle_suppresses_rank: bool = models.BooleanField(default=False)
    use_mag_as_res: bool = models.BooleanField(default=False)
    min_damage_per_attack: int = models.IntegerField(default=0)
    max_inventory_size: int = models.IntegerField(default=5)
    max_inventory_weapons: int = models.IntegerField(default=5)  # FE3 and FE10 allow only 4 weapons and 4 items
    max_inventory_items: int = models.IntegerField(default=5)
    extra_skills_limit: str = models.CharField(choices=SkillLimit.choices, default=SkillLimit.NONE,
                                               max_length=maxlength(SkillLimit))
    extra_skills_quantity_limit: int = models.IntegerField(default=0)
    team_size: int = models.IntegerField(default=5)
    max_support_rank: int = models.IntegerField(choices=SupportRank.choices, default=SupportRank.A)
    support_rank_limit: int = models.IntegerField(default=5)  # 0 if RankedSupports aren't allowed, -1 if infinite
    bond_support_behavior: str = models.CharField(choices=BondSupportBehavior.choices, default=BondSupportBehavior.NONE,
                                                  max_length=maxlength(BondSupportBehavior))
    ranked_support_behavior: str = models.CharField(choices=RankedSupportBehavior.choices,
                                                    default=RankedSupportBehavior.GBA_AFFINITY,
                                                    max_length=maxlength(RankedSupportBehavior))
    affinity_types: str = models.CharField(choices=AffinityTypes.choices, default=AffinityTypes.GBA,
                                           max_length=maxlength(AffinityTypes))

    def __str__(self):
        return f"{self.abbrev} - {self.name}"


class FireEmblemGameRoute(models.Model):
    id: models.IntegerField(primary_key=True)
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=255)
    mutually_exclusive = models.ManyToManyField('self')

    def __str__(self):
        return f"{self.game}!{self.name} ({self.id})"
