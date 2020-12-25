"""
file: arena.py

Contains the core of the API for interacting with the arena function of FEArena
"""
import logging
import random
import jsonschema
import string
import threading
from typing import Dict, List, Union
from time import sleep
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from ...models.play.GameFormat import GameFormat, VictoryCondition
from . import schemas
from . import actions as arena_actions
from .helper import tear_down_arena, save_arena
from .. import skills
from ...models.play.ActiveArena import ActiveArena
from ...models.play.ActiveUnit import ActiveUnit
from ...models.play import conversions
from ...models.play.MatchRequest import MatchRequest
from ...models.build.BuiltTeam import BuiltTeam


ARENA_ID_SET = string.ascii_letters + string.digits + '_'
MATCH_CHECK_INTERVAL = 10.0


def check_for_matches():
    """
    Preiodically checks whether there are outstanding match requests that can be honored,
    and starts matches as applicable.
    """
    while True:
        match_requests = {}
        for mr in MatchRequest.objects.filter(arena_id=None):
            match_requests \
                .setdefault(mr.game_format.name, {}) \
                .setdefault(mr.num_players, []) \
                .append(mr)
        for fmt_name, dct in match_requests.items():
            for players, reqs in dct.items():
                while len(reqs) >= players:
                    go_reqs: List[MatchRequest] = [reqs.pop(0) for _ in range(players)]
                    arena: ActiveArena = start_arena(fmt_name, [req.team_id for req in go_reqs])
                    for req in go_reqs:
                        req.arena_id = arena.id
                        req.save()
        sleep(MATCH_CHECK_INTERVAL)


threading.Thread(target=check_for_matches, daemon=True).start()


def request_match(user: User, req_info: Dict) -> int:
    """
    If the user is already requesting a match with the given number of players, returns
    False, which should indicate to return a 304 Not Modified (i.e. still waiting).
    Otherwise, adds the user to the arena requests, and returns a 200.
    :param user: user requesting the match
    :param req_info: a request conforming to the request_match_schema in api.arena.schemas
    :return: a request_id that should be queried in the future
    """
    # validate
    if MatchRequest.objects.filter(by=user, arena_id=None).count() > 0:
        raise ValueError(f"User is already requesting a game. Wait for that to finsih.")
    try:
        jsonschema.validate(instance=req_info, schema=schemas.request_match_schema)
    except ValueError as e:
        raise ValueError(f"Invalid request format - must include keys 'players', 'format_name', 'team_id'") from e
    players = req_info['players']
    format_name = req_info['format']
    team_id = req_info['team_id']
    if not (2 <= players <= 4):
        raise ValueError(f"Only 2-4 player games are allowed")
    try:
        game_format = GameFormat.objects.get(name=format_name)
    except ObjectDoesNotExist:
        raise ValueError(f"Invalid game format")
    if BuiltTeam.objects.filter(owned_by=user, id=team_id) == 0:
        raise ValueError(f"This user does not own the team they're trying to use, or the team does not exist")
    # generate request id
    request: MatchRequest = MatchRequest.objects.create(
        by=user,
        team_id=team_id,
        game_format=game_format,
        num_players=players,
    )
    return request.id


def check_request_status(user: User, request_id: int) -> Union[None, str]:
    """
    If the user's match hasn't started yet, returns None. If the user's match has
    started and is in progress or finished, returns the id of the arena.
    If the user hasn't made a match request with this ID, raises a ValueError.
    :param user: user whose match to check
    :param request_id: request_id of the match the user wants to check the status of
    :return: None if the match hasn't started yet, or the id of an ActiveArena if it has
    """
    try:
        request: MatchRequest = MatchRequest.objects.get(by=user, id=request_id)
        if request.arena_id:
            return request.arena_id
        else:
            return None
    except ObjectDoesNotExist:
        raise ValueError(f"User {user.username} did not make a match request with id {request_id}")


def get_arena_info(arena_id: str) -> Dict:
    """
    Returns a representation of the requested ActiveArena object
    :param arena_id: id of arena to fetch
    :return: A JSON representation of the ActiveArena
    """
    try:
        return ActiveArena.objects.get(id=arena_id).to_dict()
    except ObjectDoesNotExist:
        raise ValueError(f"Arena has expired, or may never have existed")


def start_arena(format_name: str, team_ids: List[int]) -> ActiveArena:
    """
    Creates/saves a new ActiveArena object with the given BuiltTeams as competitors, and returns it. The
    new ActiveArena object will contain ActiveTeam objects, constructed from the BuiltTeam objects.
    An arena must contain at least two teams, but may contain up to four, which is the maximum.
    :param format_name: the mechanics to use for this fight
    :param team_ids: a list of BuiltTeam ids, containing 2 to 4 elements inclusive.
    :return: an ActiveArena object, initialized with the given teams and saved to the database
    """
    # validate
    try:
        game_format: GameFormat = GameFormat.objects.get(name=format_name)
    except ObjectDoesNotExist:
        raise ValueError(f"Format '{format_name}' does not exist")
    if not (2 <= len(team_ids) <= 4):
        raise ValueError(f"Must have 2-4 teams to start an arena battle")
    teams: List[BuiltTeam] = []
    for team_id in team_ids:
        try:
            team: BuiltTeam = BuiltTeam.objects.get(id=team_id)
            teams.append(team)
            if game_format.validated and team.units.filter(validated=False).count() > 0:
                raise ValueError(f"At least one unit on this team is not validated, and so is invalid for this format")
        except ObjectDoesNotExist:
            raise ValueError(f"BuiltTeam with id {team_id} does not exist")
    random.shuffle(teams)
    active_teams = {
        vname: conversions.ActiveTeam_from_BuiltTeam(team)
        for vname, team in zip(["team0", "team1", "team2", "team3"], teams)
    }
    arena: ActiveArena = ActiveArena.objects.create(
        game=game_format.game,
        game_format=game_format,
        **active_teams,
        id=''.join(random.choices(ARENA_ID_SET, k=20))
    )
    logging.debug(f"""Created new arena using teams {
        ', '.join(f'{team.owned_by.username}[{team.name}]' for team in teams)
    } with mechanics from {game_format.game.name}, with format {game_format.name}, victory condition '{
    game_format.victory}'""")
    return arena


def process_phase(user: User, arena_id: str, action: Dict):
    """
    Processes a user's single action for a particular phase. If it is not the user's turn, the action does not
    conform to the correct schema, or any object IDs are incorrect, raises a ValueError.
    :param user: the user whose phase it is
    :param arena_id: the arena in which it is this user's phase
    :param action: an instruction for a unit to move or do something, conforming to the `action_input_schema`
        (see documentation for api.arena.schemas)
    :return: a summary of the end result of the above actions, conforming to the `action_output_schema`
        (see documentation for api.arena.schemas)
    """
    # validate request
    try:
        arena: ActiveArena = ActiveArena.objects.get(id=arena_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Nonexistent arena: {arena_id}")
    if user != arena.current_team().template.owned_by:
        raise ValueError(f"{user.username}, it's not your turn! " 
                         f"It's {arena.current_team().template.owned_by.username}'s turn. Be patient")
    try:
        jsonschema.validate(instance=action, schema=schemas.action_input_schema)
    except ValueError as e:
        raise ValueError("Action does not conform to the action_input_schema") from e
    try:
        unit: ActiveUnit = arena.current_team().units.get(id=action['unit'])
    except ObjectDoesNotExist:
        raise ValueError(f"The unit with id {action['unit']} does not belong to this user")
    # process the whole beginning of the turn, because in arena mode only one unit can actually move per turn
    # it is expected that this is done on the #client-side automatically, before sending command to server
    result = [{"action": "begin_turn"}]
    for team_unit in arena.current_team().units.all():
        result += skills.turn_start_all(
            skills.accumulate(
                personal=team_unit.template.unit,
                unit_class=team_unit.template.unit_class,
                active_weapons=team_unit.weapons.all(),
                active_items=team_unit.items.all(),
                extra=[*team_unit.template.extra_skills.all(), *team_unit.temp_skills.all()],
            ), team_unit, arena)
    # note: the actions are executed sequentially, and the methods in arena_actions will mutate both
    # the unit and the arena passed to them, in addition to adding to the result. If the actions are in
    # an invalid order (e.g. 'equip' after 'attack'), then not all of them will be processed. The #client
    # should not allow this to happen.
    for act in action['actions']:
        result += arena_actions.execute_action(arena, unit, act)
        if arena.turn_should_end:
            break
    # execute unit_end_turn before actually checking whether the overall turn should end
    # to accommodate for things like Canto to give the user another chance
    result += skills.unit_turn_end_all(
        skills.accumulate(
            personal=unit.template.unit,
            unit_class=unit.template.unit_class,
            active_weapons=unit.weapons.all(),
            active_items=unit.items.all(),
            extra=[*unit.template.extra_skills.all(), *unit.temp_skills.all()]
        ), unit, arena, result
    )
    battle_over = False
    if arena.turn_should_end:
        for team_unit in arena.current_team().units.all():
            result += skills.turn_end_all(
                skills.accumulate(
                    personal=team_unit.template.unit,
                    unit_class=team_unit.template.unit_class,
                    active_weapons=team_unit.weapons.all(),
                    active_items=team_unit.items.all(),
                    extra=[*team_unit.template.extra_skills.all(), *unit.temp_skills.all()]
                ), unit, arena
            )
        result.append({"action": "end_turn"})
        # advance arena phase, and possibly turn
        # check if battle is over
        if sum(team.units.all().count() == 0 for team in arena.teams()) <= 1:
            try:
                surviving_team = next(team for team in arena.teams() if team.units.all().count() > 0)
                # give the winner their points
                for unit in surviving_team.units.all():
                    surviving_team.score += 30
                    surviving_team.save()
                    result.append({
                        "action": "ponts_for_survival",
                        "unit": unit.id,
                        "team": surviving_team.id
                    })
            except StopIteration:
                surviving_team = None
            if arena.game_format.victory == VictoryCondition.POINTS:
                winning_team = max(arena.teams(), key=lambda t: t.score)
            else:  # arena.game.format.victory == VictoryCondition.SURVIVAL:
                winning_team = surviving_team
            result.append({
                "action": "victory",
                "team": winning_team.id if winning_team else None,
                "turns": arena.turn
            })
            battle_over = True
            arena.game_over = True
        else:
            phase_msg = arena.advance_phase()
            result += phase_msg
            arena.turn_should_end = False
    else:
        result.append({"action": "continue_turn"})
    # wind-down database objects, as applicable
    # first, unit, in case unit is supposed to have died by now, since we won't be using it anymore
    # (unit should already have been removed from the team containing it
    if unit.current_hp <= 0:
        logging.debug(f"Deleting ActiveUnit {unit.id} from database")
        unit.delete()
    # next, either save the current state of the arena, or tear it down, depending on whether
    # someone distinctly won the battle
    logging.debug(f"Processed actions from user {user.username} for arena {arena.id}")
    if battle_over:
        tear_down_arena(arena)  # will set a 15-minute timer
    else:
        save_arena(arena)
    # finally, return result of phase
    # this time we return the FULL action_output_schema, not just the action part of it, for once
    output = {"changes": result}
    try:
        jsonschema.validate(instance=output, schema=schemas.action_output_schema)
    except jsonschema.ValidationError as e:
        logging.warning(f"Output for this action set does not conform to the action_output_schema. "
                        f"User={user.username}; Arena={arena.id}; action={action}; return={output}; error={e}")
    return output
