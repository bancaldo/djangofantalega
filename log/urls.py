# noinspection PyUnresolvedReferences
from django.conf.urls import url
# noinspection PyUnresolvedReferences
from django.contrib import admin
from log import views as log_views
from django.contrib.auth import views as auth_views  # auth system


urlpatterns = [
    url(r'^login/$', auth_views.login,
        {'template_name': 'registration/login.html'},
        name='django.contrib.auth.views.login'),  # auth system
    url(r'^logout/$', auth_views.logout,
        {'template_name': 'registration/logged_out.html'},
        name='logout'),  # auth system
    url(r'^registration/$', log_views.register_user, name='registration'),
    url(r'^registration/success/$', log_views.register_success,
        name='reg_success'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$', log_views.activate,
        name='activate'),
    url(r'^expired/$', log_views.activation_link_expired, name='expired'),
    ]
