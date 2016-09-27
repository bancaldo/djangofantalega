# noinspection PyUnresolvedReferences
from django.shortcuts import render, redirect
from .models import League, Team, Player, Trade, Match
from .forms import AuctionPlayer, TradeForm
# noinspection PyUnresolvedReferences
from django.contrib import messages
from fantalega.scripts.calendar import create_season


# Create your views here.
def index(request):
    return render(request, 'fantalega/index.html')

def leagues(request):
    leagues = League.objects.order_by('-name')  ## - is for descendng order
    context = {'leagues': leagues,}
    return render(request, 'fantalega/leagues.html', context)

def league_details(request, league_id):
    league = League.objects.get(id=int(league_id))
    teams = league.team_set.all()
    context = {'league': league, 'teams': teams}
    return render(request, 'fantalega/league.html', context)

def teams(request):
    teams = Team.objects.order_by('name')
    context = {'teams': teams}
    return render(request, 'fantalega/teams.html', context)

def team_details(request, team_id):
    team = Team.objects.get(id=int(team_id))
    context = {'team': team}
    return render(request, 'fantalega/team.html', context)

def players(request):
    players = Player.objects.order_by('code')
    context = {'players': players,}
    return render(request, 'fantalega/players.html', context)

def player_details(request, player_id):
    player = Player.objects.get(id=int(player_id))
    context = {'player': player}
    return render(request, 'fantalega/player.html', context)

def auction(request, league_id):
    league = League.objects.get(pk=int(league_id))
    players = [(p.code, p.name) for p in Player.objects.all() if not p.team]
    teams = [(team.id, team.name) for team in league.team_set.all()]
    if request.method == "POST":
        form = AuctionPlayer(request.POST, initial={'players': players,
                                                    'teams': teams})
        if form.is_valid():
            player_code = form.cleaned_data['player']
            player = Player.get_by_code(int(player_code))
            auction_value = form.cleaned_data['auction_value']
            team_id = form.cleaned_data['team']
            team = Team.objects.get(pk=team_id)
            remaining_players = league.max_players() - team.player_set.count()
            budget_remaining = int(team.budget) - int(auction_value) - \
                               remaining_players
            if budget_remaining > 0:
                player.team = team
                player.auction_value = auction_value
                player.save()
                team.budget -= auction_value
                team.save()
                messages.add_message(request, messages.SUCCESS,
                    'Auction operation [ %s - %s ] stored!' % (player.name,
                                                               team.name))
            else:
                messages.add_message(request, messages.ERROR,
                    "Not enough budget: budget: %s, auction price %s, "
                    "remaining players %s" % (team.budget, auction_value,
                                              remaining_players))
            return redirect('auction', league.id)
    else:
        form = AuctionPlayer(initial={'players': players, 'teams': teams})
    return render(request, 'fantalega/auction.html',
                  {'form': form, 'players': players, 'teams': teams})

def trade(request, team_id):
    team = Team.objects.get(pk=int(team_id))
    players = [(p.code, "%s - %s" %(p.name, p.role))
               for p in team.player_set.all()]
    others = [(p.code, "%s - %s" % (p.name, p.role))
               for p in Player.objects.order_by('name')if p.team]
    if request.method == "POST":
        form = TradeForm(request.POST, initial={'players': players,
                                                'others': others})
        if form.is_valid():
            player_out_code = form.cleaned_data['player_out']
            player_out = Player.get_by_code(int(player_out_code))
            player_in_code = form.cleaned_data['player_in']
            player_in = Player.get_by_code(int(player_in_code))
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
                                         direction="OUT")
                    Trade.objects.create(player=player_in, team=team,
                                         direction="IN")
                    Trade.objects.create(player=player_out, team=other_team,
                                         direction="IN")
                    Trade.objects.create(player=player_in, team=other_team,
                                         direction="OUT")
                    messages.add_message(request, messages.SUCCESS,
                        'Trade operation %s: --> [OUT] %s [IN] %s stored!' % (
                            team, player_out.name, player_in.name))
                    messages.add_message(request, messages.SUCCESS,
                        'Trade operation %s: --> [OUT] %s [IN] %s stored!' % (
                            other_team, player_in.name, player_out.name))
                else:
                    messages.add_message(request, messages.ERROR,
                        'Players MUST have the same role, aborted!')

            else:
                messages.add_message(request, messages.ERROR,
                    "Not enough trade operations: %s [%s] and %s [%s]" % (
                        team.name, team.max_trades, other_team.name,
                        other_team.max_trades))
            return redirect('team_details', team.id)
    else:
        form = TradeForm(initial={'players': players, 'others': others})
    return render(request, 'fantalega/trade.html',
                  {'form': form, 'players': players, 'others': others,
                   'team': team})

def trades(request):
    trades = Trade.objects.all()
    context = {'trades': trades,}
    return render(request, 'fantalega/trades.html', context)


def calendar(request, league_id):
    league = League.objects.get(id=int(league_id))
    matches = league.matches.order_by('day')
    if matches:
        messages.add_message(request, messages.WARNING,
            'Calendar already exists!!')
    else:
        teams = [t for t in league.team_set.all()]
        cal = create_season(teams=teams, num=league.rounds)
        for record in cal:
            day, home_team, visit_team = record
            Match.objects.create(league=league, day=day, home_team=home_team,
                                 visit_team=visit_team)
        messages.add_message(request, messages.SUCCESS,
            'Calendar done!')
        matches = league.matches.order_by('day')

    context = {'matches': matches, 'league': league}
    return render(request, 'fantalega/calendar.html', context)
