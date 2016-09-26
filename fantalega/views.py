# noinspection PyUnresolvedReferences
from django.shortcuts import render
from .models import League, Team


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
