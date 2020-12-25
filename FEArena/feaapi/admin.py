from django.contrib import admin

# Register your models here.
from .models import core
from .models import build
from .models import play

admin.site.register(core.FireEmblemGame)
admin.site.register(core.Unit)
admin.site.register(core.Class)
admin.site.register(core.Weapon)
admin.site.register(core.Item)
admin.site.register(core.Skill)
admin.site.register(core.WeaponRankBonus)
admin.site.register(core.WeaponTriangleBonus)
admin.site.register(core.WeaponRankPointRequirement)
admin.site.register(core.BondSupport)
admin.site.register(core.RankedSupportTemplate)
admin.site.register(core.ExtraSkill)
admin.site.register(core.FireEmblemGameRoute)
admin.site.register(core.PromotionBonus)

admin.site.register(build.BuiltTeam)
admin.site.register(build.BuiltUnit)
admin.site.register(build.BuiltClass)
admin.site.register(build.BuiltWeapon)
admin.site.register(build.BuiltItem)
admin.site.register(build.RankedSupport)

admin.site.register(play.ActiveArena)
admin.site.register(play.ActiveTeam)
admin.site.register(play.ActiveUnit)
admin.site.register(play.ActiveItem)
admin.site.register(play.ActiveWeapon)
admin.site.register(play.GameFormat)
admin.site.register(play.SkillData)
admin.site.register(play.MatchRequest)
