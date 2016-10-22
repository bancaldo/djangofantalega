# noinspection PyUnresolvedReferences
from django.shortcuts import render, redirect, get_object_or_404
from .models import League, Team, Player, Trade, Match, Evaluation
from .models import Lineup, LineupsPlayers
from .forms import AuctionPlayer, TradeForm, UploadVotesForm, UploadLineupForm
# noinspection PyUnresolvedReferences
from django.contrib import messages
from fantalega.scripts.calendar import create_season
from datetime import datetime
from fantalega.scripts.calc import LineupHandler, get_final, lineups_data
from django.contrib.auth.decorators import login_required
from fantalega.forms import RegistrationForm
from django.contrib.auth.models import User


@login_required
def index(request):
    return render(request, 'fantalega/index.html')


@login_required
def leagues(request):
    context = {'leagues': League.objects.order_by('-name')}
    return render(request, 'fantalega/leagues.html', context)


@login_required
def league_details(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    league_teams = league.team_set.all()
    days = [d['day'] for d in
            Evaluation.objects.order_by('day').values('day').distinct()]
    if request.GET.get('auction'):
        return redirect('auction', league.id)
    if request.GET.get('calendar'):
        return redirect('calendar', league.id)
    if request.GET.get('upload votes'):
        return redirect('upload_votes', league.id)
    if request.GET.get('matches'):
        return redirect('matches', league.id)
    if request.GET.get('chart'):
        return redirect('chart', league.id)
    if request.GET.get('trades'):
        return redirect('trades', league.id)
    context = {'league': league, 'teams': league_teams,
               'days': days, 'user': request.user}
    return render(request, 'fantalega/league.html', context)


@login_required
def team_details(request, league_id, team_id):
    league = get_object_or_404(League, pk=int(league_id))
    team = get_object_or_404(Team, pk=int(team_id))
    lineups = Lineup.objects.filter(team=team, league=league).order_by('day')
    context = {'team': team, 'lineups': lineups,
               'user': request.user, 'league': league}
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    if request.GET.get('new lineup'):
        return redirect('upload_lineup', league.id, team.id)
    if request.GET.get('new trade'):
        return redirect('trade', league.id, team.id)
    return render(request, 'fantalega/team.html', context)


@login_required
def players(request):
    sorted_players = Player.objects.order_by('code')
    context = {'players': sorted_players}
    return render(request, 'fantalega/players.html', context)


@login_required
def player_details(request, player_id):
    player = Player.objects.get(id=int(player_id))
    votes = player.player_votes.all()
    context = {'player': player, 'votes': votes}
    return render(request, 'fantalega/player.html', context)


@login_required
def auction(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    free_players = [(p.code, p.name) for p in
                    Player.objects.filter(season=league.season).all()
                    if not p.team]
    league_teams = [(team.id, team.name) for team in league.team_set.all()]
    if request.method == "POST":
        form = AuctionPlayer(request.POST, initial={'players': free_players,
                                                    'teams': league_teams,
                                                    'league': league})
        if form.is_valid():
            player_code = form.cleaned_data['player']
            player = Player.get_by_code(int(player_code), season=league.season)
            auction_value = form.cleaned_data['auction_value']
            team_id = form.cleaned_data['team']
            team = Team.objects.get(pk=int(team_id))
            remaining_players = league.max_players() - team.player_set.count()
            budget_remaining = int(team.budget) - int(auction_value) - \
                remaining_players
            if budget_remaining > 0:
                player.team = team
                player.auction_value = auction_value
                player.save()
                team.budget -= auction_value
                team.save()
                messages.success(request,
                                 'Auction operation [ %s - %s ] stored!' %
                                 (player.name, team.name))
            else:
                messages.error(request,
                               "Not enough budget: budget: %s, "
                               "auction price %s, remaining players %s" %
                               (team.budget, auction_value, remaining_players))
            return redirect('auction', league.id)
    else:
        form = AuctionPlayer(initial={'players': free_players,
                                      'teams': league_teams, 'league': league})
    return render(request, 'fantalega/auction.html',
                  {'form': form, 'players': free_players,
                   'teams': league_teams, 'league': league}, )


@login_required
def trade(request, league_id, team_id):
    league = get_object_or_404(League, pk=int(league_id))
    team = get_object_or_404(Team, pk=int(team_id))
    if request.GET.get('back_to_team_details'):
        return redirect('team_details', league.id, team.id)
    team_players = [(p.code, "%s - %s" % (p.name, p.role))
                    for p in team.player_set.all()]
    others = [(p.code, "%s - %s" % (p.name, p.role))
              for p in Player.objects.order_by('name')if p.team]
    if request.method == "POST":
        form = TradeForm(request.POST, initial={'players': team_players,
                                                'others': others,
                                                'league': league})
        if form.is_valid():
            player_out_code = form.cleaned_data['player_out']
            player_out = Player.get_by_code(int(player_out_code),
                                            season=league.season)
            player_in_code = form.cleaned_data['player_in']
            player_in = Player.get_by_code(int(player_in_code),
                                           season=league.season)
            team.max_trades -= 1
            other_team = player_in.team
            other_team.max_trades -= 1
            if team.max_trades > 0 and other_team.max_trades > 0:
                player_in.team = team
                player_out.team = other_team
                if player_in.role == player_out.role:
                    player_in.save()
                    player_out.save()
                    team.save()
                    other_team.save()
                    Trade.objects.create(player=player_out, team=team,
                                         direction="OUT", league=league)
                    Trade.objects.create(player=player_in, team=team,
                                         direction="IN", league=league)
                    Trade.objects.create(player=player_out, team=other_team,
                                         direction="IN", league=league)
                    Trade.objects.create(player=player_in, team=other_team,
                                         direction="OUT", league=league)
                    messages.success(request,
                                     'Trade operation %s: --> '
                                     '[OUT] %s [IN] %s stored!' %
                                     (team, player_out.name, player_in.name))
                    messages.success(request,
                                     'Trade operation %s: --> '
                                     '[OUT] %s [IN] %s stored!' %
                                     (other_team, player_in.name,
                                      player_out.name))
                else:
                    messages.error(request,
                                   'Players MUST have the same role, aborted!')

            else:
                messages.error(request,
                               "Not enough trade operations: "
                               "%s [%s] and %s [%s]" %
                               (team.name, team.max_trades, other_team.name,
                                other_team.max_trades))
            return redirect('team_details', league.id, team.id)
    else:
        form = TradeForm(initial={'players': team_players, 'others': others,
                                  'league': league})
    return render(request, 'fantalega/trade.html',
                  {'form': form, 'players': team_players, 'others': others,
                   'team': team, 'league': league})


@login_required
def trades(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    context = {'trades': Trade.objects.all(), 'league': league}
    return render(request, 'fantalega/trades.html', context)


@login_required
def calendar(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    league_matches = league.matches.order_by('day')
    days = [d['day'] for d in Match.objects.filter(
            league=league).values('day').distinct()]
    if league_matches:
        messages.warning(request, 'Calendar already exists!!')
    else:
        league_teams = [t for t in league.team_set.all()]
        cal = create_season(teams=league_teams, num=league.rounds)
        for record in cal:
            day, home_team, visit_team = record
            Match.objects.create(league=league, day=day, home_team=home_team,
                                 visit_team=visit_team)
        messages.success(request, 'Calendar done!')
        league_matches = league.matches.order_by('day')

    context = {'matches': league_matches, 'league': league, 'days': days}
    return render(request, 'fantalega/calendar.html', context)


@login_required
def vote(request, league_id, day):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    votes = Evaluation.objects.filter(league=league, day=day).all()
    context = {'votes': votes, 'day': day, 'league': league}
    return render(request, 'fantalega/vote.html', context)


@login_required
def upload_votes(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    if request.method == "POST":
        form = UploadVotesForm(request.POST, request.FILES)
        if form.is_valid():
            day = form.cleaned_data['day']
            dict_season = dict(form.fields['season'].choices)
            season = dict_season[int(form.cleaned_data['season'])]
            file_in = request.FILES['file_in']
            Evaluation.upload(path=file_in, day=day, league=league,
                              season=season)
            messages.success(request, 'votes uploaded!')
            return redirect('league_details', league.id)
    else:
        form = UploadVotesForm()
    return render(request, 'fantalega/upload_votes.html',
                  {'form': form, 'league': league})


@login_required
def lineup_details(request, league_id, team_id, day):
    league = get_object_or_404(League, pk=int(league_id))
    total = 0.0
    team = get_object_or_404(Team, pk=int(team_id))
    offset = team.leagues.all()[0].offset
    fantaday = int(day) + int(offset)
    lineup = team.team_lineups.filter(day=int(day)).first()
    lineup_players = LineupsPlayers.get_sorted_lineup(lineup)
    holders = [l_p.player for l_p in lineup_players[:11]]
    substitutes = [s_p.player for s_p in lineup_players[11:]]
    d_votes = {code: (fv, v) for code, fv, v in
               [Evaluation.get_evaluations(day=(int(day) + offset),
                                           code=p.code) for p in holders]}
    if request.GET.get('modify lineup'):
        return redirect('lineup_edit', league.id, team.id, day)
    if request.GET.get('calculate'):
        try:
            handler = LineupHandler(lineup, int(day), int(offset))
            total = handler.get_pts()
        except AttributeError:
            messages.error(request, 'No pts available: '
                                    'lineups or evaluations are missing, '
                                    'check in calendar...')
            total = ''

    context = {'team': team, 'holders': holders, 'substitutes': substitutes,
               'lineup': lineup, 'day': day, 'd_votes': d_votes,
               'fantaday': fantaday, 'total': total, 'league': league}
    return render(request, 'fantalega/lineup.html', context)


@login_required
def upload_lineup(request, league_id, team_id, day=None):
    league = get_object_or_404(League, pk=int(league_id))
    modules = [(1, '343'), (2, '352'), (3, '442'), (4, '433'), (5, '451'),
               (6, '532'), (7, '541')]
    team = get_object_or_404(Team, pk=int(team_id))
    if request.GET.get('back_to_team_details'):
        return redirect('team_details', league.id, team.id)
    team_players = [(p.code, "%s [%s]" % (p.name, p.role))
                    for p in team.player_set.all()]
    if request.method == "POST":
        form = UploadLineupForm(request.POST,
                                initial={'players': team_players, 'team': team,
                                         'modules': modules, 'day': day,
                                         'league': league})
        if form.is_valid():
            day = form.cleaned_data['day']
            holders = [Player.get_by_code(int(code), season=league.season)
                       for code in form.cleaned_data['holders']]
            substitutes = [Player.get_by_code(int(code), season=league.season)
                           for code in [form.cleaned_data['substitute_%s' % n]
                           for n in range(1, 11)]]
            error = form.check_holders()
            if error:
                messages.error(request, error)
            else:
                messages.success(request, "Lineup correct!")
                lineup = Lineup.objects.filter(
                    team=team, day=day, league=league).first()
                if not lineup:
                    lineup = Lineup.objects.create(team=team, day=day,
                                                   league=league,
                                                   timestamp=datetime.now())
                    for pos, player in enumerate((holders + substitutes), 1):
                        LineupsPlayers.objects.create(
                            position=pos, lineup=lineup, player=player)
                messages.success(request, 'Lineup uploaded!')
                return redirect('team_details', league_id, team_id)
    else:
        form = UploadLineupForm(initial={'players': team_players, 'team': team,
                                         'modules': modules, 'day': day,
                                         'league': league})
    return render(request, 'fantalega/upload_lineup.html',
                  {'form': form, 'players': team_players, 'team': team,
                   'league': league})


@login_required
def lineup_edit(request, league_id, team_id, day):
    league = get_object_or_404(League, pk=int(league_id))
    modules = [(1, '343'), (2, '352'), (3, '442'), (4, '433'), (5, '451'),
               (6, '532'), (7, '541')]
    team = get_object_or_404(Team, pk=int(team_id))
    if request.GET.get('back_to_team_details'):
        return redirect('team_details', league.id, team.id)
#    lineup = team.team_lineups.filter(day=day).first()
    lineup = Lineup.objects.filter(team=team, league=league, day=day).first()
    team_players = [(p.code, "%s [%s]" % (p.name, p.role))
                    for p in team.player_set.all()]
    if request.method == "POST":
        form = UploadLineupForm(request.POST,
                                initial={'players': team_players, 'team': team,
                                         'modules': modules, 'day': day,
                                         'league': league})
        if form.is_valid():
            day = form.cleaned_data['day']
#            module_id = form.cleaned_data['module']
#            module = dict(form.fields['module'].choices)[int(module_id)]
            holders = [Player.get_by_code(int(code), season=league.season)
                       for code in form.cleaned_data['holders']]
            substitutes = [Player.get_by_code(int(code), season=league.season)
                           for code in [form.cleaned_data['substitute_%s' % n]
                           for n in range(1, 11)]]
            error = form.check_holders()
            if error:
                messages.error(request, error)
            else:
                messages.success(request, "Lineup correct!")
                lineup.timestamp = datetime.now()
                lineup.save()
                for pos, player in enumerate((holders + substitutes), 1):
                    lu = LineupsPlayers.objects.filter(
                        lineup=lineup, position=int(pos)).first()
                    lu.player = player
                    lu.save()
                    print "[INFO] Lineup %s (%s) -> Player %s pos %s upgraded!"\
                          % (team.name, day, player.name, pos)

                messages.success(request, 'Lineup upgraded!')
                return redirect('team_details', team_id)
    else:
        form = UploadLineupForm(initial={'players': team_players, 'team': team,
                                         'modules': modules, 'day': day,
                                         'league': league})
        for n, player in enumerate(lineup.players.all()[11:], 1):
            form.fields['substitute_%s' % n].initial = player.code
        form.fields['holders'].initial = [p.code for p in
                                          lineup.players.all()[:11]]
    return render(request, 'fantalega/upload_lineup.html',
                  {'form': form, 'players': team_players, 'team': team,
                   'league': league})


@login_required
def matches(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    league_matches = league.matches
    days = [d['day'] for d in Match.objects.filter(
        league=league).values('day').distinct()]
    d_calendar = Match.calendar_to_dict(league)
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    context = {'league': league, 'd_calendar': d_calendar,
               'days': days, 'matches': league_matches}
    return render(request, 'fantalega/matches.html', context)


@login_required
def match_details(request, league_id, day):
    league = get_object_or_404(League, pk=int(league_id))
    if request.GET.get('back_to_calendar'):
        return redirect('matches', league.id)
    league_matches = league.matches.filter(day=int(day))
    missing_lineups = []
    if request.GET.get('calculate'):
        for match in league_matches:
            home_lineup = match.home_team.team_lineups.filter(
                day=int(day)).first()
            visit_lineup = match.visit_team.team_lineups.filter(
                day=int(day)).first()
            offset_day = int(day) + league.offset
            if Evaluation.objects.filter(day=offset_day).count() == 0:
                messages.error(request,
                               'day %s evaluations missing, import them!' %
                               offset_day)
                return redirect('matches', league.id)

            if home_lineup and visit_lineup:
                h_home = LineupHandler(home_lineup, int(day),
                                       int(league.offset))
                h_visit = LineupHandler(visit_lineup, int(day),
                                        int(league.offset))
                home_pts = h_home.get_pts() + 2
                visit_pts = h_visit.get_pts()
                home_goals, visit_goals = get_final(home_pts, visit_pts)
                data = lineups_data(home_goals, visit_goals)
                home_lineup.pts = home_pts
                home_lineup.save()
                visit_lineup.pts = visit_pts
                visit_lineup.save()
                for lineup, prefix in [(home_lineup, 'h'), (visit_lineup, 'v')]:
                    lineup.won = data.get("%sw" % prefix)
                    lineup.matched = data.get("%sm" % prefix)
                    lineup.lost = data.get("%sl" % prefix)
                    lineup.goals_made = data.get("%sgm" % prefix)
                    lineup.goals_conceded = data.get("%sgc" % prefix)
                    lineup.save()
            else:
                if not home_lineup:
                    missing_lineups.append(match.home_team.name)
                if not visit_lineup:
                    missing_lineups.append(match.visit_team.name)
        if not missing_lineups:
            messages.success(request, 'All Lineup values are upgraded!')
        else:
            if len(missing_lineups) == league.team_set.count():
                message = 'No lineups uploaded for day %s yet' % day
            else:
                message = 'Some Lineups are missing: %s' % \
                          ', '.join(missing_lineups)
            messages.error(request, message)
        return redirect('matches', league.id)
    context = {'league': league, 'matches': league_matches, 'day': day}
    return render(request, 'fantalega/match.html', context)


@login_required
def chart(request, league_id):
    league = get_object_or_404(League, pk=int(league_id))
    league_teams = league.team_set.all()
    if request.GET.get('back_to_teams'):
        return redirect('league_details', league.id)
    lineups_values = []
    for team in league_teams:
        lineups = [lineup for lineup in
                   Lineup.objects.filter(league=league, team=team).all()
                   if lineup.pts]
        won = sum([lineup.won for lineup in lineups])
        matched = sum([lineup.matched for lineup in lineups])
        lost = sum([lineup.lost for lineup in lineups])
        gm = sum([lineup.goals_made for lineup in lineups])
        gc = sum([lineup.goals_conceded for lineup in lineups])
        tot_pts = sum([lineup.pts for lineup in lineups])
        tot = won * 3 + matched
        lineups_values.append((team, tot, won, matched, lost, gm, gc, tot_pts))
    lineups_values.sort(key=lambda x: (x[1], x[6]), reverse=True)
    context = {'league': league, 'lineups_values': lineups_values}
    return render(request, 'fantalega/chart.html', context)


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'])
            messages.success(request, "Welcome %s now you can login" %
                             user.username)
            return redirect ('reg_success')
        return render(request, 'registration/registration_form.html', context)
    else:
        form = RegistrationForm()
        context = {'form': form}
    return render(request, 'registration/registration_form.html', context)


def register_success(request):
    return render(request, 'registration/success.html')

# send email
# go to https://www.google.com/settings/security/lesssecureapps
# click on active

# from django.core.mail import EmailMessage
#
# email = EmailMessage('test', 'content', 'bancaldo <bancaldo@gmail.com>',
#                      ['bancaldo@gmail.com'],)
# email.send()