from django.test import TestCase
from fantalega.models import Player, Lineup, Evaluation, League, Team
from fantalega.models import LeaguesTeams, LineupsPlayers, Season
from django.utils import timezone
from datetime import datetime
from fantalega.scripts.calc import LineupHandler, BadInputError
from fantalega.scripts.calc import convert_pts_to_goals, get_final
# Create your tests here.


class LineupTestCase(TestCase):
    def setUp(self):
        g = 'goalkeeper'
        d = 'defender'
        m = 'midfielder'
        f = 'forward'
        self.players = ((112, 'consigli', g), (356, 'rodriguez', d),
                        (415, 'bastos', d), (357, 'romagnoli', d),
                        (303, 'izzo', d), (510, 'banega', m),
                        (647, 'parolo', m), (601, 'krejci', m),
                        (825, 'dybala', f), (971, 'milik', f),
                        (802, 'adriano', f), (136, 'pegolo', g),
                        (413, 'milic', d), (397, 'zukanovic', d),
                        (220, 'astori', d), (516, 'benassi', m),
                        (721, 'aquilani', m), (584, 'hetemaj', m),
                        (581, 'hallfredsson', m), (914, 'pjaca', f),
                        (865, 'meggiorini', f))
        self.vals = [(112, 6.0), (356, 6.0), (415, 6.0), (357, 6.0), (303, 6.0),
                     (510, 6.0), (647, 6.0), (601, 6.0), (825, 6.0), (971, 6.0),
                     (802, 6.0), (136, 6.0), (413, 0.0), (397, 6.0), (220, 6.0),
                     (516, 0.0), (721, 0.0), (584, 0.0), (581, 0.0), (914, 0.0),
                     (865, 0.0)]
        self.season = Season.objects.create(name="test_season")
        league = League.objects.create(season=self.season,
                                       name="test_league", budget=500,
                                       max_trades=3, max_goalkeepers=3,
                                       max_defenders=8, max_midfielders=8,
                                       max_forwards=6, rounds=4, offset=0)
        
        for code, name, role in self.players:
            Player.objects.create(season=self.season, name=name,
                                  code=code, cost=0,
                                  auction_value=0, role=role)
        for code, vote in self.vals:
            player = Player.objects.filter(code=code, season=self.season).first()
            Evaluation.objects.create(season=self.season,
                                      player=player, day=1, fanta_value=vote,
                                      net_value=vote, cost=0)
        self.team = Team.objects.create(name='test_team', budget=league.budget,
                                        max_trades=league.max_trades)
        LeaguesTeams.objects.create(team=self.team, league=league)
        self.lineup = Lineup.objects.create(team=self.team, day=1,
                                            timestamp=timezone.now(), league=league)
        for pos, code in enumerate([code for code, name, r in self.players], 1):
            player = Player.objects.filter(code=code, season=self.season).first()
            LineupsPlayers.objects.create(lineup=self.lineup, player=player,
                                          position=pos)
        self.handler = LineupHandler(lineup=self.lineup, day=1, league=league)

    def test_holder_and_substitutes(self):
        """Lineup is correctly splitted"""
        self.assertEqual(len(self.handler.holders), 11)
        self.assertEqual(len(self.handler.substitutes), 10)

    def test_no_subs_needed(self):
        """Lineup doesn't need substitutions with all holders evaluated"""
        self.assertEqual(self.handler.need_substitutions(), False)

    def test_if_no_subs_needed_get_result(self):
        """If no substitutions needed get total from evaluated holders"""
        self.assertEqual(self.handler.get_pts(), sum([val for code, val
                                                      in self.vals[:11]]) +
                         self.handler.mod)

    def test_subs_needed(self):
        """Lineup needs substitutions with one ore more holders not evaluated"""
        player = Player.get_by_code(356, self.season)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.need_substitutions(), True)

    def test_substitute_of_the_same_role_is_present(self):
        """Check if a substitute with the same role is available"""
        player = Player.get_by_code(356, self.season)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.is_same_role_available(player), True)

    def test_substitute_of_a_different_role_is_present(self):
        """Check if a substitute with a different role is available"""
        player = Player.get_by_code(356, self.season)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.is_substitute_available(), True)

    def test_if_substitute_has_got_the_same_role(self):
        """Check if a the candidated substitute has got the same role"""
        player = Player.get_by_code(356, self.season)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        candidate = self.handler.get_same_role_substitute(player)
        self.assertTrue(player.role == candidate.role)

    def test_different_role_substitute(self):
        """Check if a the candidated substitute with different role
        is available """
        for code, vote in ((397, 0.0), (220, 0.0), (356, 0.0), (584, 7.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        candidate = self.handler.get_substitute(Player.get_by_code(356, self.season))
        self.assertFalse(candidate.role == 'goalkeeper')

    def test_one_substitution(self):
        """Check if 1 non-evaluated player is substituted"""
        for code, vote in ((397, 8.0), (220, 0.0), (356, 0.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 69)  # def_mod included

    def test_two_substitutions_with_same_role(self):
        """Check if 2 non-evaluated players are substituted"""
        for code, vote in ((356, 0.0), (415, 0.0),  # holders changes
                           (397, 8.0), (220, 7.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 70)  # def_mod included

    def test_three_substitutions_with_same_role(self):
        """Check if 3 non-evaluated players are substituted"""
        for code, vote in ((356, 0.0), (415, 0.0), (510, 0.0),
                           (397, 8.0), (220, 4.0), (584, 5.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 66)  # def_mod included

    def test_four_substitutions_with_same_role(self):
        """Check if 4 non-evaluated players are substituted by only 3 ones"""
        for code, vote in ((356, 0.0), (415, 0.0), (510, 0.0), (971, 0.0),
                           (397, 8.0), (220, 4.0), (584, 5.0), (914, 3.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 60)  # def_mod included

    def test_one_substitution_of_different_role(self):
        """Check if 1 non-evaluated player is substituted with
        different role and changing module"""
        for code, vote in ((721, 8.0), (220, 0.0), (356, 0.0), (397, 0.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 68)

    def test_one_substitution_of_different_role_not_ammitted_module(self):
        """Check if 1 non-evaluated player isn't substituted with
        different role that change module in an invalid one"""
        for code, vote in ((356, 0.0),  # holder change
                           (136, 0.0), (413, 0.0), (397, 0.0), (220, 0.0),
                           (516, 0.0), (721, 0.0), (584, 0.0), (581, 0.0),
                           (914, 10.0), (865, 0.0)):
            player = Player.get_by_code(code, self.season)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 60)


class PtsTestCase(TestCase):
    def test_pts_to_goals_raise_if_not_float(self):
        """Check if not-float input raises Exception"""
        self.assertRaises(BadInputError, convert_pts_to_goals, 60)

    def test_pts_to_goals(self):
        """Check if converting pts to goals is correct"""
        self.assertEqual(convert_pts_to_goals(60.0), 0)
        self.assertEqual(convert_pts_to_goals(59.0), 0)
        self.assertEqual(convert_pts_to_goals(66.0), 1)
        self.assertEqual(convert_pts_to_goals(72.0), 2)
        self.assertEqual(convert_pts_to_goals(78.0), 3)

    def test_final_result_is_correct(self):
        """Check if final result is correct"""
        self.assertEqual(get_final(59.5, 60.0), (0, 1))
        self.assertEqual(get_final(65.0, 61.0), (1, 0))
        self.assertEqual(get_final(59.0, 59.5), (1, 1))
        self.assertEqual(get_final(66.0, 65.5), (1, 0))
        self.assertEqual(get_final(72.0, 71.5), (2, 1))
        self.assertEqual(get_final(72.0, 62.0), (3, 0))
        self.assertEqual(get_final(82.0, 82.0), (3, 3))
