# noinspection PyUnresolvedReferences
from django import forms
from .models import Player, Team


class AuctionPlayer(forms.Form):
    def __init__(self, *args, **kwargs):
        dict_values = kwargs.pop('initial')
        super(AuctionPlayer, self).__init__(*args, **kwargs)

        self.fields['player'] = forms.ChoiceField(label=u'player',
                                               choices=dict_values['players'],
                                               widget=forms.Select(),
                                               required=False)
        self.fields['auction_value'] = forms.IntegerField()
        self.fields['team'] = forms.ChoiceField(label=u'team',
                                               choices=dict_values['teams'],
                                               widget=forms.Select(),
                                               required=False)
