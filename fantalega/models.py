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
