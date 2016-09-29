# noinspection PyUnresolvedReferences
from django.contrib import admin
from .models import League, LeaguesTeams, Team, Player, Trade, Match, Evaluation
from .models import Lineup, LineupsPlayers


# Register your models here.
admin.site.register(League)
admin.site.register(LeaguesTeams)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Trade)
admin.site.register(Match)
admin.site.register(Evaluation)
admin.site.register(Lineup)
admin.site.register(LineupsPlayers)
