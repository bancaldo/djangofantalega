from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from django.db import models

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

    def max_players(self):
        return self.max_goalkeepers + self.max_defenders + \
            self.max_midfielders + self.max_forwards

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=32)
    budget = models.IntegerField()
    max_trades = models.IntegerField()
    leagues = models.ManyToManyField(League, through='LeaguesTeams')

    def set_home(self):
        self.home = True

    def set_visit(self):
        self.home = False

    def __str__(self):
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


class Player(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=32)
    real_team = models.CharField(max_length=3)
    cost = models.IntegerField()
    auction_value = models.IntegerField()
    role = models.CharField(max_length=16)
    team = models.ForeignKey(Team, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_by_code(code):
        return Player.objects.filter(code=int(code)).first()

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

    @staticmethod
    def upload(path):
        with open(path) as data:
            for record in data:  # nnn|PLAYER_NAME|REAL_TEAM|x|y|n
                code, name, real_team, fv, v, cost = record.strip().split("|")
                player = Player.get_by_code(code)
                role = Player.code_to_role(code.strip())
                if not player:
                    Player.objects.create(name=name, code=code, role=role,
                                          real_team=real_team, cost=cost,
                                          auction_value=0)
                    print "[INFO] Creating %s %s" % (code, name)
                else:
                    player.cost = cost
                    player.real_team = real_team
                    player.save()
                    print "[INFO] Upgrading %s %s" % (code, name)
        print "[INFO] Players uploading done!"


class Trade(models.Model):
    player = models.ForeignKey(Player)
    team = models.ForeignKey(Team)
    direction = models.CharField(max_length=3)  # IN or OUT value

    def __str__(self):
        return "[%s] %s: %s" % (self.direction, self.team.name,
                                self.player.name)


class Match (models.Model):
    league = models.ForeignKey(League, related_name='matches')
    day = models.IntegerField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    visit_team = models.ForeignKey(Team, related_name='visit_team')

    def __str__(self):
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


class Evaluation(models.Model):
    league = models.ForeignKey(League, related_name='league_votes')
    player = models.ForeignKey(Player, related_name='player_votes')
    day = models.IntegerField()
    net_value = models.FloatField()
    fanta_value = models.FloatField()
    cost = models.IntegerField()

    def __str__(self):
        return "[%s] %s" % (self.day, self.player.name)

    @staticmethod
    def get_evaluations(day, code):
        """get_evaluations(self, day, code) -> fanta_value, net_value
           code: Player.code
           day: lineup.day + league.offset
        """
        player = Player.objects.filter(code=int(code)).first()
        evaluation = Evaluation.objects.filter(day=day, player=player).first()
        if evaluation and player:
            return code, evaluation.fanta_value, evaluation.net_value
        else:
            return code, None, None


    @staticmethod
    def upload(path, day, league):
        # with open(path) as data:  # for shell string-file-path upload
        with path as data:  # for InMemoryUploadedFile object upload
            for record in data:  # nnn|PLAYER_NAME|REAL_TEAM|x|y|n
                code, name, real_team, fv, v, cost = record.strip().split("|")
                player = Player.get_by_code(code)
                role = Player.code_to_role(code.strip())
                if not player:
                    player = Player(name=name, code=code, role=role,
                                    real_team=real_team, cost=cost,
                                    auction_value=0)
                    print "[INFO] Creating %s %s" % (code, name)
                else:
                    player.cost = cost
                    player.real_team = real_team
                    print "[INFO] Upgrading %s %s" % (code, name)
                player.save()
                # storing evaluation
                evaluation = Evaluation.objects.filter(day=day,
                                                       player=player).first()
                if evaluation:
                    evaluation.net_value = v
                    evaluation.fanta_value = fv
                    evaluation.cost = cost
                    evaluation.save()
                    print "[INFO] Upgrading values day: %s player %s" % (
                        day, player.name)
                else:
                    Evaluation.objects.create(day=day, player=player, cost=cost,
                                              net_value=v, fanta_value=fv,
                                              league=league)
                    print "[INFO] Creating values day: %s player %s" % (
                        day, player.name)
        print "[INFO] Evaluation uploading done!"


class Lineup (models.Model):
    team = models.ForeignKey(Team, related_name='team_lineups')
    players = models.ManyToManyField(Player, through='LineupsPlayers',
                                     related_name='player_lineups')
    timestamp = models.DateField()
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

    def __str__(self):
        return "[%s] %s" % (self.day, self.team.name)


# M2M secondary Association object
class LineupsPlayers(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE)
    position = models.IntegerField()

    @staticmethod
    def get_sorted_lineup(lineup):
        return LineupsPlayers.objects.filter(
            lineup=lineup).order_by('position').all()
