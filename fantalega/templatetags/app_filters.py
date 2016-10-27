# noinspection PyUnresolvedReferences
from django import template
from django.utils.safestring import mark_safe
from fantalega.models import Lineup, Player, Evaluation


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


@register.filter(name='need_calc')
def need_calc(league, day):
    for team in league.team_set.all():
        if not team.team_lineups.filter(day=day).first():
            return False
    return True


@register.filter(name='has_pts')
def has_pts(league, day):
    lineups = [Lineup.objects.filter(team=team, league=league, day=day).first()
               for team in league.team_set.all() if
               Lineup.objects.filter(team=team, league=league, day=day).first()]
    calculated_lineups = [l.pts for l in lineups if l.pts > 0]
    return len(calculated_lineups) == len(league.team_set.all())


@register.filter(name='get_total')
def get_total(team, day):
    lineup = team.team_lineups.filter(day=int(day)).first()
    return lineup.pts if lineup else '0.0: Lineup missing'


@register.filter(name='get_goals')
def get_goals(team, day):
    lineup = team.team_lineups.filter(day=int(day)).first()
    if lineup:
        return lineup.goals_made
    else:
        return "ND"


@register.filter(name='get_evaluated')
def get_evaluated(dict_evaluated, key):
    data = dict_evaluated.get(key)
    if data:
        return data[0]
    else:
        return []
#    return dict_evaluated.get(key)


@register.filter(name='get_defense_mod')
def get_defense_mod(dict_evaluated, key):
    data = dict_evaluated.get(key)
    if data:
        return data[1]
    else:
        return 0.0


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


@register.filter(name='is_defender')
def is_defender(player):
    obj_player = Player.objects.filter(name=player).first()
    if 200 < obj_player.code < 500:
        return mark_safe('<font color="#cc66ff">%s</font>' % player)
    else:
        return player


@register.filter(name='color_by_role')
def color_by_role(player):
    if player.role.lower() == 'goalkeeper':
        color = 'blue'
    elif player.role.lower() == 'defender':
        color = 'orange'
    elif player.role.lower() == 'midfielder':
        color = 'green'
    else:
        color = 'purple'
    new_string = '<font color="%s">%s</font>' % (color, player.name.lower())
    return mark_safe(new_string)


@register.filter(name='get_played')
def get_played(player, code):
    obj_player = Player.objects.filter(name=player, code=code).first()
    played = [e for e in Evaluation.objects.filter(player=obj_player).all()
              if e.fanta_value > 0.0 ]
    return len(played)


@register.filter(name='total_to_buy')
def get_played(team, league):
    player_bought = team.player_set.count()
    remain = league.max_players() - player_bought
    color = "green" if not remain else "red"
    return mark_safe('<b><font color="%s">%s</font></b>' % (color, remain))


@register.filter(name='gk_to_buy')
def gk_to_buy(team, league):
    gk_bought = team.player_set.filter(role='goalkeeper').count()
    remain = league.max_goalkeepers - gk_bought
    color = "green" if not remain else "red"
    return mark_safe('<b><font color="%s">%s</font></b>' % (color, remain))


@register.filter(name='def_to_buy')
def def_to_buy(team, league):
    def_bought = team.player_set.filter(role='defender').count()
    remain = league.max_defenders - def_bought
    color = "green" if not remain else "red"
    return mark_safe('<b><font color="%s">%s</font></b>' % (color, remain))


@register.filter(name='mid_to_buy')
def mid_to_buy(team, league):
    mid_bought = team.player_set.filter(role='midfielder').count()
    remain = league.max_midfielders - mid_bought
    color = "green" if not remain else "red"
    return mark_safe('<b><font color="%s">%s</font></b>' % (color, remain))


@register.filter(name='forw_to_buy')
def forw_to_buy(team, league):
    forw_bought = team.player_set.filter(role='forward').count()
    remain = league.max_forwards - forw_bought
    color = "green" if not remain else "red"
    return mark_safe('<b><font color="%s">%s</font></b>' % (color, remain))


@register.filter(name='get_avg')
def get_avg(player, code):
    obj_player = Player.objects.filter(name=player, code=code).first()
    fanta_values = [e.fanta_value for e
                    in Evaluation.objects.filter(player=obj_player).all()
                    if e.fanta_value > 0.0 ]
    return sum(fanta_values)/len(fanta_values)


@register.assignment_tag
def get_matches(matches, day):
    return matches.filter(day=day)


@register.assignment_tag
def get_bootstrap_alert_msg_css_name(tags):
    return 'danger' if tags == 'error' else tags


