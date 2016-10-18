# noinspection PyUnresolvedReferences
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name='get_fvote')
def get_fvote(player, day):
    evaluation = player.player_votes.filter(day=int(day)).first()
    if evaluation:
        return '%s' % float(evaluation.fanta_value)
    else:
        return '0.0'


@register.filter(name='get_vote')
def get_vote(player, day):
    evaluation = player.player_votes.filter(day=int(day)).first()
    if evaluation:
        return '%s' % float(evaluation.net_value)
    else:
        return '0.0'


@register.filter(name='get_pts')
def get_pts(team, day):
    lineup = team.team_lineups.filter(day=int(day)).first()
    if lineup:
        return lineup.pts
    else:
        return "ND"


@register.filter(name='get_goals')
def get_goals(team, day):
    lineup = team.team_lineups.filter(day=int(day)).first()
    if lineup:
        return lineup.goals_made
    else:
        return "ND"


@register.filter(name='pts_filter')
def pts_filter(value):
    if value:
        if float(value) <= 60:
            color = 'e60000'
        elif 60 < float(value) <= 72:
            color = 'cc66ff'
        else:
            color = '009933'
        new_string = '<b><font color="#%s">%s</font></b>' % (color, value)
        return mark_safe(new_string)
    else:
        return value


@register.assignment_tag
def get_matches(matches, day):
    return matches.filter(day=day)


@register.assignment_tag
def get_bootstrap_alert_msg_css_name(tags):
    return 'danger' if tags == 'error' else tags
