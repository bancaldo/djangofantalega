# noinspection PyUnresolvedReferences
from django import forms
from .models import Player
# noinspection PyUnresolvedReferences
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User


class AuctionPlayer(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dict_values = kwargs.pop('initial')
        super(AuctionPlayer, self).__init__(*args, **kwargs)

        self.fields['player'] = forms.ChoiceField(
            label=u'player', choices=self.dict_values['players'],
            widget=forms.Select(), required=False)
        self.fields['auction_value'] = forms.IntegerField()
        self.fields['team'] = forms.ChoiceField(
            label=u'team', choices=self.dict_values['teams'],
            widget=forms.Select(), required=False)


class TradeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dict_values = kwargs.pop('initial')
        super(TradeForm, self).__init__(*args, **kwargs)
        self.fields['player_out'] = forms.ChoiceField(
            label=u'OUT', choices=self.dict_values['players'],
            widget=forms.Select(), required=False)
        self.fields['player_in'] = forms.ChoiceField(
            label=u'IN', choices=self.dict_values['others'],
            widget=forms.Select(), required=False)


class UploadVotesForm(forms.Form):
    day = forms.IntegerField()
    seasons = enumerate(['%s-%s' % (n, n + 1) for n in range(2016, 2030)],)
    season = forms.ChoiceField(label=u'season', choices=seasons,
                               widget=forms.Select(),)
    file_in = forms.FileField()


class UploadLineupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dict_values = kwargs.pop('initial')
        super(UploadLineupForm, self).__init__(*args, **kwargs)
        self.fields['module'] = forms.ChoiceField(
            label=u'module', choices=self.dict_values['modules'],
            widget=forms.Select())
        self.fields['day'] = forms.IntegerField(initial=self.dict_values['day'])
        self.fields['holders'] = forms.MultipleChoiceField(
            choices=self.dict_values['players'],
            widget=forms.CheckboxSelectMultiple())
        for n in range(1, 11):
            self.fields['substitute_%s' % n] = forms.ChoiceField(
                label=u'substitute %s' % n, choices=self.dict_values['players'],
                widget=forms.Select(), required=False)

    def check_holders(self):
            error = ''
            data = self.cleaned_data['holders']
            substitutes = [self.cleaned_data.get('substitute_%s' % n)
                           for n in range(1, 11)]
            if len(data) != 11:
                return "holder players number is wrong!"
            module = dict(self.fields['module'].choices)[
                int(self.cleaned_data['module'])]
            mod_defs, mod_mids, mod_forws = module
            goalkeepers = len([code for code in data if int(code) < 200])
            defenders = len([code for code in data if 200 < int(code) < 500])
            midfielders = len([code for code in data if 500 < int(code) < 800])
            forwarders = len([code for code in data if int(code) > 800])
            if goalkeepers > 1:
                return "To many goalkeepers!"
            if defenders != int(mod_defs):
                return "number of defenders doesn't match module!"
            if midfielders != int(mod_mids):
                return "number of midfielders doesn't match module!"
            if forwarders != int(mod_forws):
                return "number of forwarders doesn't match module!"
            for code in substitutes:
                player = Player.get_by_code(int(code),
                                            self.dict_values['league'].season)
                if code in data:
                    return "substitute %s is in holders!" % player.name
                if substitutes.count(code) > 1:
                    return "Duplicate substitute %s in list!" % player.name
            return error


class TeamSellPlayersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dict_values = kwargs.pop('initial')
        super(TeamSellPlayersForm, self).__init__(*args, **kwargs)
        self.fields['team_players'] = forms.MultipleChoiceField(
            choices=self.dict_values['team_players'],
            widget=forms.CheckboxSelectMultiple())