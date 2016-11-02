# noinspection PyUnresolvedReferences
from django.conf.urls import url
# noinspection PyUnresolvedReferences
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    # league urls
    url(r'^leagues/$', views.leagues, name='leagues'),
    url(r'^leagues/(?P<league_id>[0-9]+)/$', views.league_details,
        name='league_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/calendar$', views.calendar,
        name='calendar'),
    url(r'^leagues/(?P<league_id>[0-9]+)/chart$',
        views.chart, name='chart'),
    # team urls
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)/$',
        views.team_details, name='team_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/'
        r'(?P<team_id>[0-9]+)/player_sale$', views.sale, name='sale'),
    # players urls
    url(r'^players/$', views.players, name='players'),
    url(r'^players/(?P<player_id>[0-9]+)/$', views.player_details,
        name='player_details'),
    # auction urls
    url(r'^leagues/(?P<league_id>[0-9]+)/auction$', views.auction,
        name='auction'),
    url(r'^leagues/(?P<league_id>[0-9]+)/auction/summary$',
        views.auction_summary, name='auction_summary'),
    # trade urls
    url(r'^leagues/(?P<league_id>[0-9]+)/trades/$',
        views.trades, name='trades'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)/trade$',
        views.trade, name='trade'),
    # votes urls
    url(r'^leagues/(?P<league_id>[0-9]+)/votes/(?P<day>[0-9]+)/$',
        views.vote, name='vote'),
    url(r'^leagues/(?P<league_id>[0-9]+)/upload$', views.upload_votes,
        name='upload_votes'),
    # lineup urls
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/'
        r'(?P<team_id>[0-9]+)/lineup/upload$', views.upload_lineup,
        name='upload_lineup'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)'
        r'/lineup/(?P<day>[0-9]+)/$',
        views.lineup_details, name='lineup_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/teams/(?P<team_id>[0-9]+)'
        r'/lineup/(?P<day>[0-9]+)/edit$',
        views.lineup_edit, name='lineup_edit'),
    # matches urls
    url(r'^leagues/(?P<league_id>[0-9]+)/matches$', views.matches,
        name='matches'),
    url(r'^leagues/(?P<league_id>[0-9]+)/matches/(?P<day>[0-9]+)/$',
        views.match_details, name='match_details'),
    url(r'^leagues/(?P<league_id>[0-9]+)/matches/(?P<day>[0-9]+)/deadline$',
        views.match_deadline, name='match_deadline'),
]
