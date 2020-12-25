from django.db import models
from .._util import BaseModel
from typing import List, Dict
from .ActiveTeam import ActiveTeam
from .ActiveUnit import ActiveUnit
from .GameFormat import GameFormat
from ..core.Game import FireEmblemGame


class ActiveArena(BaseModel):
    id: str = models.CharField(primary_key=True, max_length=20)
    team0: ActiveTeam = models.ForeignKey(ActiveTeam, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='+')
    team1: ActiveTeam = models.ForeignKey(ActiveTeam, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='+')
    team2: ActiveTeam = models.ForeignKey(ActiveTeam, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='+')
    team3: ActiveTeam = models.ForeignKey(ActiveTeam, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='+')
    game: FireEmblemGame = models.ForeignKey(FireEmblemGame, on_delete=models.CASCADE)
    game_format: GameFormat = models.ForeignKey(GameFormat, on_delete=models.CASCADE)
    turn: int = models.IntegerField(default=1)
    phase: int = models.IntegerField(default=0)
    game_over: bool = models.BooleanField(default=False)

    # this field included for internal use only. Actions will tell the arena whether the turn should end.
    turn_should_end: bool = models.BooleanField(default=False)

    def advance_phase(self) -> List[Dict]:
        """
        Advances the current phase, moving to the next team that isn't null or empty.
        :return: phase change messages, conforming to api.arena.schemas
        """
        output = []
        while True:
            self.phase += 1
            if self.phase == 4:
                self.turn += 1
                self.phase = 0
                output.append({"action": "change_turn", "turn": self.turn})
            team = self.current_team()
            if team and team.units.all().count() > 0:
                break
        output.append({"action": "change_phase", "phase": self.phase})
        return output

    def teams(self):
        """
        :return: a list of all this arena's non-null ActiveTeams
        """
        return [team for team in [self.team0, self.team1, self.team2, self.team3] if team]

    def current_team(self) -> ActiveTeam:
        """
        :return: the ActiveTeam corresponding to the arena's current phase
        """
        return [self.team0, self.team1, self.team2, self.team3][self.phase]

    def team_containing_unit(self, unit: ActiveUnit) -> ActiveTeam:
        """
        Returns the first team containing the given unit. Throws a ValueError if not found.
        :param unit: ActiveUnit to search for
        :return: the team containing the given unit
        """
        for team in self.teams():
            if unit in team.units.all():
                return team
        raise ValueError(f"Unit with id {unit.id} is not in any of this arena's teams")

    def to_dict(self):
        """
        Returns this arena, in JSON format, conforming to the appropriate schema defined in
        api.arena.schemas
        """
        return {
            'id': self.id,
            'game': self.game.abbrev,
            'format': self.game_format.name,
            'teams': [
                team.to_dict() for team in [self.team0, self.team1, self.team2, self.team3] if team
            ],
            'turn': self.turn,
            'phase': self.phase
        }
