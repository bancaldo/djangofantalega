# noinspection PyUnresolvedReferences
from django.contrib import admin
from .models import League, Team, Player

# Register your models here.
admin.site.register(League)
admin.site.register(Team)
admin.site.register(Player)
