# noinspection PyUnresolvedReferences
from django.shortcuts import render, redirect
from .models import League, Team, Player
from .forms import AuctionPlayer
# noinspection PyUnresolvedReferences
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'history/index.html')

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
