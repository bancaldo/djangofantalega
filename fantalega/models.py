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
            for record in data:  ## nnn|PLAYER_NAME|REAL_TEAM|x|y|n
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


#>>> ringo = Person.objects.create(name="Ringo Starr")
#>>> paul = Person.objects.create(name="Paul McCartney")
#>>> beatles = Group.objects.create(name="The Beatles")
#>>> m1 = Membership(person=ringo, group=beatles,
#... date_joined=date(1962, 8, 16),
#... invite_reason="Needed a new drummer.")
#>>> m1.save()
#>>> beatles.members.all()
#<QuerySet [<Person: Ringo Starr>]>
#>>> ringo.group_set.all()
#<QuerySet [<Group: The Beatles>]>
#>>> m2 = Membership.objects.create(person=paul, group=beatles,
#... date_joined=date(1960, 8, 1),
#... invite_reason="Wanted to form a band.")
#>>> beatles.members.all()