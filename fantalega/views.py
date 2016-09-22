# noinspection PyUnresolvedReferences
from django.shortcuts import render
from .models import League


# Create your views here.
def index(request):
    return render(request, 'history/index.html')

def leagues(request):
    leagues = League.objects.order_by('-name')  ## - is for descendng order
    context = {'leagues': leagues,}
    return render(request, 'fantalega/leagues.html', context)

def league_details(request, league_id):
    league = League.objects.get(id=int(league_id))
    context = {'league': league}
    return render(request, 'fantalega/league.html', context)
