"""djangosite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# noinspection PyUnresolvedReferences
from django.conf.urls import url, include
# noinspection PyUnresolvedReferences
from django.contrib import admin
from django.contrib.auth import views as auth_views  # auth system


urlpatterns = [
    url(r'^fantalega/', include('fantalega.urls')),
    url(r'^login/$', auth_views.login,
        {'template_name': 'registration/login.html'},
        name='django.contrib.auth.views.login'),  # auth system
    #url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'template_name': 'registration/logged_out.html'},
        name='logout'),  # auth system
    url(r'^admin/', admin.site.urls),
]
