from django.db import models
from django.contrib.auth.models import User
from .._util import BaseModel
from .GameFormat import GameFormat
from datetime import datetime
from .ActiveArena import ActiveArena
from ..build.BuiltTeam import BuiltTeam


class MatchRequest(BaseModel):
    id: int = models.AutoField(primary_key=True)
    by: User = models.ForeignKey(User, on_delete=models.CASCADE)
    game_format: GameFormat = models.ForeignKey(GameFormat, on_delete=models.CASCADE)
    team_id: int = models.IntegerField()
    num_players: int = models.IntegerField()
    last_updated: datetime = models.DateTimeField(auto_now=True)
    arena_id: str = models.CharField(max_length=20, default=None, null=True, blank=True)
