"""
file: teambuilder/build.py

Implements processes that relate to building a team to use in an
Arena battle
"""
import jsonschema
from jsonschema.exceptions import ValidationError
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from typing import Dict, List
from ...models.build.BuiltUnit import BuiltUnit
from ...models.build.BuiltTeam import BuiltTeam
from ...models.build.BuiltClass import BuiltClass
from ...models.build.BuiltWeapon import BuiltWeapon
from ...models.build.BuiltItem import BuiltItem
from ...models.build.RankedSupport import RankedSupport
from ...models.core.RankedSupportTemplate import RankedSupportTemplate
from ...models.core.Unit import Unit
from ...models.core.Class import Class
from ...models.core.Item import Item
from ...models.core.Weapon import Weapon
from ...models.core.Skill import Skill
from ...models.core.ExtraSkillAttainment import ExtraSkill
from ...models.core.Game import FireEmblemGame, ChangeClassBehavior, PromotionBonus, SupportRank
from .helper import *
from . import validator, schemas
from .. import skills
from ..calc import ranks


def build_team(user: User, instructions: Dict) -> Dict:
    """
    Using the given instructions for building a team, constructs, saves, and returns
    the ID of a BuiltTeam
    :param user: user for whom the team is being built
    :param instructions: instructions for building the team, conforming to the
        build_team_schema in api.teambuilder.schemas
    :return: the completed BuiltTeam, as a dict conforming to the
        built_team_schema in api.teambuilder.schemas
    """
    # validate request
    try:
        jsonschema.validate(instance=instructions, schema=schemas.build_team_schema)
    except ValueError as e:
        raise ValueError("Request does not conform to the build_team_schema") from e
    try:
        game: FireEmblemGame = FireEmblemGame.objects.get(abbrev=instructions["game"])
    except ObjectDoesNotExist:
        raise ValueError(f"There's no Fire Emblem game abbreviated {instructions['game']}")
    if len(instructions["units"]) > game.team_size and instructions.get("validate", True):
        raise ValueError(f"Too many units on team ({len(instructions['units'])} > {game.team_size})")
    # create the team and stack units onto it
    team: BuiltTeam = BuiltTeam.objects.create(
        name=instructions["name"],
        owned_by=user
    )
    i = 0
    try:
        for unit_instr in instructions["units"]:
            # cut off after 5 units no matter what, unless user has selected unlimited
            if i >= game.team_size and instructions.get("limit", True):
                break
            unit = build_unit(game, unit_instr, instructions.get("validate", True), instructions.get("limit", True))
            team.units.add(unit)
        validator.validate_unit_routes(instructions.get("validate", True), list(team.units.all()))
        # add default supports
        for unit in team.units.all():
            for support_template in RankedSupportTemplate.objects.filter(
                    unit=unit.unit,
                    default_rank__gt=SupportRank.NONE,
                    supported_by__in=[u.unit for u in team.units.all()]
            ):
                validator.validate_support(instructions.get("validate", True), game, unit,
                                           support_template.supported_by, support_template.default_rank)
                RankedSupport.objects.create(
                    unit=unit,
                    supported_by=support_template.supported_by,
                    rank=support_template.default_rank
                )
        validator.validate_support_combinations(instructions.get("validate", True), list(team.units.all()))
        # add affinity, if applicable
        if 'tactician_rank' in instructions and 'tactician_affinity' in instructions:
            validator.validate_tactician(instructions.get("validate", True), game, instructions['tactician_rank'],
                                         instructions['tactician_affinity'])
            team.tactician_rank = instructions['tactician_rank']
            team.tactician_affinity = instructions['tactician_affinity']
        # save completed built_team
        team.save()
        logging.debug(f"Created BuiltTeam with id {team.id}")
        ret = team.to_dict()
        try:
            jsonschema.validate(instance=ret, schema=schemas.built_team_schema)
        except ValidationError as e:
            logging.error(f"Response does not conform to the built_team_schema. Response: {ret}; error: {str(e)}")
        return ret
    except ValueError:
        delete_built_team(team)
        raise


def build_unit(game: FireEmblemGame, instructions: Dict, validate: bool = True, apply_limits: bool = True) -> BuiltUnit:
    """
    Using the given instructions, constructs, saves, and returns a new BuiltUnit.
    :param game: The game whose mechanics are to be used for building this unit
    :param instructions: a set of teambuilding instructions conforming to the
        build_unit_schema in api.teambuilder.schemas
    :param validate: Should this build be validated w.r.t. the given game as we go,
        using teambuilder.validate functions. If True, will raise a ValueError
        should validation fail.
    :param apply_limits: Should the normal game limits (e.g. level max, stat caps)
        apply to this BuiltUnit, assuming validation doesn't trigger or is turned off?
    :return: a BuiltUnit constructed from the ground up based on the instructions
    """
    # get initial unit state
    base_unit: Unit = Unit.objects.get(id=instructions["base_unit"])
    current_class: BuiltClass = BuiltClass.objects.create(template=base_unit.initial_class)
    unit: BuiltUnit = BuiltUnit.objects.create(
        nickname=instructions['nickname'],
        unit=base_unit,
        unit_class=current_class.template,
        unit_level=base_unit.base_lv,
        from_instructions=instructions,
        validated=validate,
        limited=apply_limits,
    )
    unit.from_instructions['id'] = unit.id
    skills_from_class = sorted(ExtraSkill.objects.filter(unit_class=current_class.template), key=lambda s: s.level)
    available_extra_skills = set(sfc.skill for sfc in skills_from_class if sfc.level <= unit.unit_level)
    applicable_items: List[Item] = []  # growth-boosting items, skillbooks, etc. Statboosters have their own command.
    # don't add to class history until we switch off this class, or at the end
    # now, walk through instructions and progressively make modifications
    for mod in instructions["modifications"]:
        if mod["action"] == "level_up":
            validator.validate_level_up(validate, unit)
            if not apply_limits or unit.unit_level < current_class.template.maximum_level:
                unit.unit_level += 1
                current_class.levels += 1
            # learn a skill from the new class if you don't already know it
            try:
                available_extra_skills.add(next(s for s in skills_from_class if s not in available_extra_skills))
            except StopIteration:
                pass
        elif mod["action"] == "boost_stat":
            # the game does not prevent you from using items while over your max, so neither will we.
            # at calculation-time, this will get truncated down to unit- or class-max
            apply_stat_boost(unit, mod["stat"], mod["points"])
        elif mod["action"] == "build_support":
            # first get the unit in question
            try:
                support_unit = Unit.objects.get(id=mod["with"])
            except ObjectDoesNotExist:
                raise ValueError(f"Cannot support with unit {mod['with']} which does not exist")
            # validate the support relationship
            validator.validate_support(validate, game, unit, support_unit)
            # get and add to the support relationship
            try:
                support: RankedSupport = RankedSupport.objects.get(unit=unit, supported_by=support_unit)
                support.rank += 1
                support.save()
            except ObjectDoesNotExist:
                RankedSupport.objects.create(unit=unit, support_unit=support_unit, rank=1)
        elif mod["action"] == "boost_weapon_rank":
            # validate that the user has any weapon rank in this weapon type. If not, it can't be boosted
            validator.validate_boost_weapon_rank(validate, game, unit, mod["weapon_type"])
            # first apply the boost, and second set the unit's favored weapon type if applicable
            apply_rank_boost(game, unit, mod["weapon_type"], mod["points"], apply_limits)
        elif mod["action"] == "promote":
            try:
                new_class: Class = Class.objects.get(id=mod["into"])
            except ObjectDoesNotExist:
                raise ValueError(f"Cannot promote unit into class with id {mod['into']}, because it does not exist")
            validator.validate_promotion(validate, unit, current_class.template, new_class)
            # add current class to past classes, and update current_class
            if game.promotion_bonuses == PromotionBonus.SEPARATE:
                apply_promotion_bonuses(game, unit, current_class.template, new_class, apply_limits)
            current_class.save()
            unit.unit_class_history.add(current_class)
            current_class = BuiltClass.objects.create(template=new_class)
            unit.unit_class = current_class.template

            skills_from_class = sorted(ExtraSkill.objects.filter(unit_class=current_class.template),
                                       key=lambda s: s.level)
            if game.promotion_behavior == ChangeClassBehavior.RESET_LEVEL:
                unit.unit_level = 1
            available_extra_skills |= set(sfc.skill for sfc in skills_from_class if sfc.level == unit.unit_level)
        elif mod["action"] == "change_class":
            try:
                new_class = Class.objects.get(id=mod["into"])
            except ObjectDoesNotExist:
                raise ValueError(f"Cannot change unit into class with id {mod['into']}, because it does not exist")
            validator.validate_class_change(validate, game, unit, current_class.template, new_class)
            # add current class to past classes and update
            current_class.save()
            unit.unit_class_history.add(current_class)
            current_class = BuiltClass.objects.create(template=new_class)
            unit.unit_class = current_class.template
            skills_from_class = sorted(ExtraSkill.objects.filter(unit_class=current_class.template),
                                       key=lambda s: s.level)
            if game.class_change_behavior == ChangeClassBehavior.RESET_LEVEL:
                unit.unit_level = 1
            # 3H skills should be given a level-learned of 0 or -1, as should Awakening's level 1 skills
            # this way, Fates won't learn new skills on reclass
            available_extra_skills |= set(sfc.skill for sfc in skills_from_class if sfc.level <= 0)
        elif mod["action"] == "apply_item":
            try:
                item = Item.objects.get(id=mod["item"])
            except ObjectDoesNotExist:
                raise ValueError(f"Cannot use item with id {mod['item']} that does not exist")
            applicable_items.append(item)
    # add add the unit's current class and levels to the class history
    current_class.save()
    unit.unit_class_history.add(current_class)
    # now, handle weapons and inventory
    i = 0
    validator.validate_inventory(validate, game, instructions["inventory"])
    for equipment in instructions["inventory"]:
        if equipment['kind'] == 'item':
            # mandatory validation, because ActiveItem does it too during battles
            try:
                item = Item.objects.get(id=equipment['item'])
            except ObjectDoesNotExist:
                raise ValueError(f"Inventory item with id {equipment['item']} does not exist")
            if equipment['equipped'] and not item.equippable:
                raise ValueError(f"Item {item.name} is not equippable")
            elif equipment['equipped'] and item.prf_users.all().count() > 0 and unit.unit not in item.prf_users.all():
                raise ValueError(f"Unit {unit.unit.name} cannot equip Prf item {item.name}")
            # add item to inventory
            unit.items.add(BuiltItem.objects.create(
                template=item,
                inventory_id=i,
                equipped=equipment['equipped']
            ))
        elif equipment['kind'] == 'weapon':
            # mandatory validation because ActiveWeapon does it too during battles
            try:
                weapon = Weapon.objects.get(id=equipment['weapon'])
            except ObjectDoesNotExist:
                raise ValueError(f"Inventory weapon with id {equipment['weapon']} does not exist")
            if equipment['equipped'] and not ranks.built_unit_can_equip_weapon(game, unit, weapon):
                raise ValueError(f"Unit does not have the appropriate Prf or weapon ranks to equip {weapon.name}")
            # add weapon to inventory
            unit.weapons.add(BuiltWeapon.objects.create(
                template=weapon,
                inventory_id=i,
                equipped=equipment['equipped']
            ))
        i += 1
    # apply used items to user.
    # this is optimistic, so growth-enhancing items will be retroactively assumed to have been used
    # at the lowest possible level, and will increase stats accordingly.
    skills.on_build_all(skills.accumulate(items=applicable_items), unit, available_extra_skills)
    # finally, handle extra skills
    chosen_skills = []
    for skill_id in instructions["chosen_skills"]:
        try:
            chosen_skills.append(Skill.objects.get(id=skill_id))
        except ObjectDoesNotExist:
            raise ValueError(f"Skill with id {skill_id} does not exist")
    validator.validate_extra_skills(validate, game, unit, available_extra_skills, chosen_skills)
    for skill in chosen_skills:
        unit.extra_skills.add(skill)
    # this should be everything. Save unit, and return
    save_built_unit(unit)
    logging.debug(f"Created BuiltUnit with id {unit.id}")
    return unit


def get_all_teams(user: User) -> List[Dict]:
    """
    Returns a list of all the BuiltTeam.to_dict()s with the given user as owner
    :param user: user to query with
    :return: a list of teams with this user as owner
    """
    return [team.to_dict() for team in BuiltTeam.objects.filter(owned_by=user)]


def get_team(user: User, team_id: int) -> Dict:
    """
    Returns .to_dict() of the given team, if the user owns it.
    """
    built_team: BuiltTeam = BuiltTeam.objects.get(id=team_id)
    if built_team.owned_by != user:
        raise ValueError(f"The user {user.username} does not own the team {team_id}")
    return built_team.to_dict()


def delete_team(user: User, team_id: int):
    """
    Tries to delete the given BuiltTeam from the database. Fails if it's not owned by the user.
    """
    built_team: BuiltTeam = BuiltTeam.objects.get(id=team_id)
    if built_team.owned_by != user:
        raise ValueError(f"The user {user.username} does not own the team {team_id}")
    delete_built_team(built_team)
