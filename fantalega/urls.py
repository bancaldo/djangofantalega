# noinspection PyUnresolvedReferences
from django.conf.urls import url
# noinspection PyUnresolvedReferences
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^leagues/$', views.leagues, name='leagues'),
    url(r'^leagues/(?P<league_id>[0-9]+)/$', views.league_details,
        name='league_details'),
    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/(?P<team_id>[0-9]+)/$', views.team_details,
        name='team_details'),
    url(r'^players/$', views.players, name='players'),
    url(r'^players/(?P<player_id>[0-9]+)/$', views.player_details,
        name='player_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/auction$', views.auction,
        name='auction'),
    url(r'^trades/$', views.trades, name='trades'),
    url(r'^teams/(?P<team_id>[0-9]+)/trade$', views.trade,
        name='trade'),
]
