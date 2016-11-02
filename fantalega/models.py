from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from django.db import models
from fantalega.scripts.xlstools import LineupExtractor as LEx
from django.utils import timezone
from django.contrib.auth.models import User
from fantalega.validators import validate_season_name


class Season(models.Model):
    name = models.CharField(max_length=9, validators=[validate_season_name])

    def __unicode__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=32)
    budget = models.IntegerField()
    max_trades = models.IntegerField()
    max_goalkeepers = models.IntegerField()
    max_defenders = models.IntegerField()
    max_midfielders = models.IntegerField()
    max_forwards = models.IntegerField()
    rounds = models.IntegerField()
    offset = models.IntegerField()
    season = models.ForeignKey(Season, related_name='leagues')

    def max_players(self):
        return self.max_goalkeepers + self.max_defenders + \
            self.max_midfielders + self.max_forwards

    def __unicode__(self):
        return self.name

    def get_matches_by_day(self, day):
        return self.matches.filter(day=day)


class Team(models.Model):
    name = models.CharField(max_length=32)
    budget = models.IntegerField()
    max_trades = models.IntegerField()
    user = models.OneToOneField(User, null=True, related_name='team')
    leagues = models.ManyToManyField(League, through='LeaguesTeams')

    def set_home(self):
        self.home = True

    def set_visit(self):
        self.home = False

    def __unicode__(self):
        return self.name

    @staticmethod
    def auction_upload(path):
        with open(path) as data:
            for record in data:
                name, auction_value, team_name = record.strip().split(";")
                player = Player.objects.filter(name=name.upper()).first()
                if player:
                    player.auction_value = int(auction_value)
                    team = Team.objects.filter(name=team_name).first()
                    if team:
                        player.team = team
                        team.budget -= player.auction_value
                        player.save()
                        team.save()
                        print "[INFO] Remaining Budget %s: %s" % (team.name,
                                                                  team.budget)
                        print "[INFO] Associating %s - %s" % (player.name,
                                                              team.name)
                    else:
                        print "[ERROR] Team %s not found" % team_name
                else:
                    print "[ERROR] Player %s not found" % name
            print "[INFO] Auction upload done!"


# M2M secondary Association object
class LeaguesTeams(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'League-Team Associations'


class Player(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=32)
    real_team = models.CharField(max_length=3)
    cost = models.IntegerField()
    auction_value = models.IntegerField()
    role = models.CharField(max_length=16)
    team = models.ForeignKey(Team, null=True)
    season = models.ForeignKey(Season, related_name='players')

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_by_code(code, season):
        return Player.objects.filter(code=int(code), season=season).first()

    @staticmethod
    def code_to_role(code):
        if int(code) < 200:
            return 'goalkeeper'
        elif 200 < int(code) < 500:
            return 'defender'
        elif 500 < int(code) < 800:
            return 'midfielder'
        elif int(code) > 800:
            return 'forward'
        else:
            return 'unknown'


class Trade(models.Model):
    league = models.ForeignKey(League, related_name='trades')
    player = models.ForeignKey(Player)
    team = models.ForeignKey(Team)
    direction = models.CharField(max_length=3)  # IN or OUT value

    def __unicode__(self):
        return "[%s] %s: %s" % (self.direction, self.team.name,
                                self.player.name)


class Match (models.Model):
    league = models.ForeignKey(League, related_name='matches')
    day = models.IntegerField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    visit_team = models.ForeignKey(Team, related_name='visit_team')
    dead_line = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = 'Matches'

    def __unicode__(self):
        return "[%s] %s - %s" % (self.day, self.home_team.name,
                                 self.visit_team.name)

    @staticmethod
    def calendar_to_dict(league):
        matches = league.matches.all()
        d = {match.day: [] for match in matches}
        for match in matches:
            day = match.day
            home = match.home_team
            visit = match.visit_team
            values = d[day]
            values.append(home)
            values.append(visit)
        return d

    def is_played(self):
        home_lineup = self.home_team.team_lineups.filter(day=self.day).first()
        visit_lineup = self.visit_team.team_lineups.filter(day=self.day).first()
        if not home_lineup or not visit_lineup:
            return False
        home_players = home_lineup.players.count()
        visit_players = visit_lineup.players.count()
        evaluations = Evaluation.objects.filter(
            day=self.day + self.league.offset).count()
        if home_players and visit_players and evaluations:
            return True
        else:
            return False

    @staticmethod
    def get_dead_line(league, day):
        match_query_set = Match.objects.filter(league=league, day=day)
        for match in match_query_set.all():
            if not match.dead_line:
                return None
        return match_query_set.first().dead_line


class Evaluation(models.Model):
    season = models.ForeignKey(Season, related_name='evaluations')
    player = models.ForeignKey(Player, related_name='player_votes')
    day = models.IntegerField()
    net_value = models.FloatField()
    fanta_value = models.FloatField()
    cost = models.IntegerField()

    def __unicode__(self):
        return "[%s] %s" % (self.day, self.player.name)

    @staticmethod
    def get_evaluations(day, code, season):
        """get_evaluations(self, day, code, season) -> fanta_value, net_value
           code: Player.code
           day: lineup.day + league.offset
           season: season object
        """
        player = Player.objects.filter(code=int(code), season=season).first()
        evaluation = Evaluation.objects.filter(day=day, player=player).first()
        if evaluation and player:
            return code, evaluation.fanta_value, evaluation.net_value
        else:
            return code, None, None

    @staticmethod
    def upload(path, day, season):
        # with open(path) as data:  # for shell string-file-path upload
        with path as data:  # for InMemoryUploadedFile object upload
            for record in data:  # nnn|PLAYER_NAME|REAL_TEAM|x|y|n
                code, name, real_team, fv, v, cost = record.strip().split("|")
                player = Player.get_by_code(code, season)
                role = Player.code_to_role(code.strip())
                if not player:
                    player = Player(name=name, code=code, role=role,
                                    real_team=real_team, cost=cost,
                                    auction_value=0, season=season)
                    print "[INFO] Creating %s %s" % (code, name)
                else:
                    player.cost = cost
                    player.real_team = real_team
                    print "[INFO] Upgrading %s %s" % (code, name)
                player.save()
                # storing evaluation
                evaluation = Evaluation.objects.filter(day=day, season=season,
                                                       player=player).first()
                if evaluation:
                    evaluation.net_value = v
                    evaluation.fanta_value = fv
                    evaluation.cost = cost
                    evaluation.save()
                    print "[INFO] Upgrading values day: %s player %s [%s]" % (
                        day, player.name, season.name)
                else:
                    Evaluation.objects.create(day=day, player=player, cost=cost,
                                              net_value=v, fanta_value=fv,
                                              season=season)
                    print "[INFO] Creating values day: %s player %s [%s]" % (
                        day, player.name, season.name)
        print "[INFO] Evaluation uploading done!"


class Lineup (models.Model):
    league = models.ForeignKey(League, related_name='league_lineups')
    team = models.ForeignKey(Team, related_name='team_lineups')
    players = models.ManyToManyField(Player, through='LineupsPlayers',
                                     related_name='player_lineups')
    timestamp = models.DateTimeField()
    day = models.IntegerField()
    pts = models.FloatField(null=True)
    won = models.IntegerField(null=True)
    matched = models.IntegerField(null=True)
    lost = models.IntegerField(null=True)
    goals_made = models.IntegerField(null=True)
    goals_conceded = models.IntegerField(null=True)

    def get_players_by_position(self):
        lineup_players = LineupsPlayers.query.filter(lineup=self.id).order_by(
            LineupsPlayers.position).all()
        if lineup_players:
            return [rec.player for rec in lineup_players]

    def __unicode__(self):
        return "[%s] %s" % (self.day, self.team.name)

    @staticmethod
    def upload_lineups_from_xls(path, league, day):
        for team in league.team_set.all():
            if team.team_lineups.filter(day=day).first():
                print "[INFO] Lineup of %s for day %s already exists!" %\
                    (team.name, day)
            else:
                print team
                ex = LEx(path, team.name, day)
                players = ex.extract()
                lineup = Lineup.objects.create(team=team, day=day,
                                               league=league,
                                               timestamp=timezone.now())
                for pos, player in enumerate(players, 1):
                    if player:
                        player_obj = Player.objects.filter(
                            name=player.upper(), season=league.season).first()
                    else:
                        print "[WARNING] Player %s doesn't exist" % player
                        player_obj = [p for p in team.player_set.all()
                                      if p not in lineup.players.all()][0]
                        print "[WARNING] Fill lineup with %s" % player_obj.name
                    print "[INFO] saving Player %s in db..." % player_obj
                    LineupsPlayers.objects.create(position=pos, lineup=lineup,
                                                  player=player_obj)
                print "[INFO] Lineup of %s for day %s uploaded!" %\
                    (team.name, day)


# M2M secondary Association object
class LineupsPlayers(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Lineup-Player Associations'

    @staticmethod
    def get_sorted_lineup(lineup):
        return LineupsPlayers.objects.filter(
            lineup=lineup).order_by('position').all()
