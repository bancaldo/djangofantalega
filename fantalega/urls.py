# noinspection PyUnresolvedReferences
from django.conf.urls import url
# noinspection PyUnresolvedReferences
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    # fantalega urls
    url(r'^leagues/$', views.leagues, name='leagues'),
    url(r'^leagues/(?P<league_id>[0-9]+)/$', views.league_details,
        name='league_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)/$',
        views.team_details, name='team_details'),
    url(r'^players/$', views.players, name='players'),
    url(r'^players/(?P<player_id>[0-9]+)/$', views.player_details,
        name='player_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/auction$', views.auction,
        name='auction'),
    url(r'^leagues/(?P<league_id>[0-9]+)/trades/$',
        views.trades, name='trades'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)/trade$',
        views.trade, name='trade'),
    url(r'^leagues/(?P<league_id>[0-9]+)/calendar$', views.calendar,
        name='calendar'),
    url(r'^leagues/(?P<league_id>[0-9]+)/votes/(?P<day>[0-9]+)/$',
        views.vote, name='vote'),
    url(r'^leagues/(?P<league_id>[0-9]+)/upload$', views.upload_votes,
        name='upload_votes'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/'
        r'(?P<team_id>[0-9]+)/lineup/upload$', views.upload_lineup,
        name='upload_lineup'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)'
        r'/lineup/(?P<day>[0-9]+)/$',
        views.lineup_details, name='lineup_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/matches$', views.matches,
        name='matches'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)'
        r'/lineup/(?P<day>[0-9]+)/edit$',
        views.lineup_edit, name='lineup_edit'),
    url(r'^leagues/(?P<league_id>[0-9]+)/matches/(?P<day>[0-9]+)/$',
        views.match_details, name='match_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/chart$',
        views.chart, name='chart'),
    # Registration urls
    url(r'^registration/$', views.register_user, name='registration'),
    url(r'^registration/success/$', views.register_success,
        name='reg_success'),
]
