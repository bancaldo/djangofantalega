# noinspection PyUnresolvedReferences
from django import template


register = template.Library()


@register.filter(name='get_fvote')
def get_fvote(player, day):
    evaluation = player.player_votes.filter(day=int(day)).first()
    if evaluation:
        return ('%s' % float(evaluation.fanta_value))
    else:
        return '0.0'


@register.filter(name='get_vote')
def get_vote(player, day):
    evaluation = player.player_votes.filter(day=int(day)).first()
    if evaluation:
        return ('%s' % float(evaluation.net_value))
    else:
        return '0.0'

@register.filter(name='get_pts')
def get_pts(team, day):
    lineup = team.team_lineups.filter(day=int(day)).first()
    if lineup:
        return lineup.pts
    else:
        return "ND"

