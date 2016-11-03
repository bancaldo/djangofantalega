# noinspection PyUnresolvedReferences
from django.contrib import admin
from .models import Season, League, LeaguesTeams, Team, Player, Trade
from .models import Match, Evaluation, Lineup, LineupsPlayers
from django.utils.html import format_html


# Register your models here.

class LeaguesInline(admin.TabularInline):
    model = Team.leagues.through
    extra = 0
    classes = ('collapse',)
    verbose_name = 'associated league'
    verbose_name_plural = 'associated leagues'


class TeamsInline(admin.TabularInline):
    model = Team.leagues.through
    extra = 0
    classes = ('collapse',)
    verbose_name = 'associated teams'
    verbose_name_plural = 'associated teams'


class LineupPlayersInline(admin.TabularInline):
    model = Lineup.players.through
    extra = 0
    classes = ('collapse',)


class LeagueAdmin(admin.ModelAdmin):
    inlines = [TeamsInline, ]
    fieldsets = [(None, {'fields': ['name', 'budget', 'max_trades',
                                    'rounds', 'offset']}),
                 ('season', {'fields': ['season']}),
                 ('number of Players', {'fields': ['max_goalkeepers',
                                                   'max_defenders',
                                                   'max_midfielders',
                                                   'max_forwards']}),
                 ]


class PlayersInline(admin.TabularInline):
    model = Player
    extra = 0
    classes = ('collapse',)


class TeamAdmin(admin.ModelAdmin):
    inlines = [LeaguesInline, PlayersInline]
    list_display = ('name', 'budget', 'max_trades')
    ordering = ('-budget', )


class MatchAdmin(admin.ModelAdmin):
    ordering = ('day', )
    list_display = ('day', 'home_team', 'visit_team', 'dead_line')
    list_filter = ('day', )
    list_per_page = 15


class PlayerAdmin(admin.ModelAdmin):
    ordering = ('code', )
    list_display = ('code', 'name', 'real_team', 'cost')
    list_filter = ('season', 'role', 'team')
    list_per_page = 20


class LineupAdmin(admin.ModelAdmin):
    inlines = [LineupPlayersInline, ]
    ordering = ('day', )
    list_display = ('day', 'team', 'pts')
    list_filter = ('day', 'team')
    list_per_page = 20


class TradeAdmin(admin.ModelAdmin):
    list_display = ('direction', 'colored_player', 'team')
    list_filter = ('direction', 'team')
    list_per_page = 20

    @staticmethod
    def colored_player(obj):
        colour = '013ADF' if obj.direction == 'IN' else 'FF0080'
        return format_html('<span style="color: #{};">{}</span>',
                           colour, obj.player.name)


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('day', 'player', 'fanta_value', 'net_value', 'cost')
    list_filter = ('day', 'player', 'season')
    list_per_page = 50


class LeaguesTeamsAdmin(admin.ModelAdmin):
    list_display = ('league', 'team')
    list_filter = ('league', 'team')
    list_per_page = 20


class LineupsPlayersAdmin(admin.ModelAdmin):
    ordering = ('position', )
    list_display = ('position', 'colored_player', 'get_team_name', )
    list_filter = ('lineup__day', 'lineup__team__name')
    list_per_page = 21

    @staticmethod
    def get_team_name(obj):
        return obj.lineup.team.name

    @staticmethod
    def colored_player(obj):
        colour = '013ADF' if obj.position <= 11 else 'FF0080'
        return format_html('<span style="color: #{};">{}</span>',
                           colour, obj.player.name)


admin.site.register(Season)
admin.site.register(League, LeagueAdmin)
admin.site.register(LeaguesTeams, LeaguesTeamsAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Lineup, LineupAdmin)
admin.site.register(LineupsPlayers, LineupsPlayersAdmin)
