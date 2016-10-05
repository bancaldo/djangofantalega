from django.test import TestCase
from fantalega.models import Player, Lineup, Evaluation, League, Team
from fantalega.models import LeaguesTeams, LineupsPlayers
from datetime import datetime
from fantalega.scripts.calcdev import LineupHandler
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

        league = League.objects.create(name="test_league", budget=500,
                                       max_trades=3, max_goalkeepers=3,
                                       max_defenders=8, max_midfielders=8,
                                       max_forwards=6, rounds=4, offset=2)
        for code, name, role in self.players:
            Player.objects.create(name=name, code=code, cost=0,
                                  auction_value=0, role=role)
        for code, vote in self.vals:
            player = Player.get_by_code(code)
            Evaluation.objects.create(player=player, day=1, fanta_value=vote,
                                      net_value=vote, cost=0, league=league)
        self.team = Team.objects.create(name='test_team', budget=league.budget,
                                        max_trades=league.max_trades)
        LeaguesTeams.objects.create(team=self.team, league=league)
        self.lineup = Lineup.objects.create(team=self.team, day=1,
                                            timestamp=datetime.now())
        for pos, code in enumerate([code for code, name, r in self.players], 1):
            player = Player.objects.filter(code=code).first()
            LineupsPlayers.objects.create(lineup=self.lineup, player=player,
                                          position=pos)
        self.handler = LineupHandler(self.lineup)

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
                                                      in self.vals[:11]]))
    def test_subs_needed(self):
        """Lineup needs substitutions with one ore more holders not evaluated"""
        player = Player.get_by_code(356)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.need_substitutions(), True)

    def test_substitute_of_the_same_role_is_present(self):
        """Check if a substitute with the same role is available"""
        player = Player.get_by_code(356)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.is_same_role_available(player), True)

    def test_substitute_of_a_different_role_is_present(self):
        """Check if a substitute with a different role is available"""
        player = Player.get_by_code(356)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        self.assertEqual(self.handler.is_substitute_available(player), True)

    def test_if_substitute_has_got_the_same_role(self):
        """Check if a the candidated substitute has got the same role"""
        player = Player.get_by_code(356)
        ev = Evaluation.objects.filter(player=player).first()
        ev.fanta_value = 0.0
        ev.save()
        candidate = self.handler.get_same_role_substitute(player)
        self.assertTrue(player.role==candidate.role)

    def test_different_role_substitute(self):
        """Check if a the candidated substitute with different role
        is available """
        for code, vote in ((397, 0.0), (220, 0.0), (356, 0.0), (584, 7.0)):
            player = Player.get_by_code(code)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        candidate = self.handler.get_substitute(Player.get_by_code(356))
        self.assertFalse(candidate.role=='goalkeeper')

    def test_one_substitution(self):
        """Check if 1 non-evaluated player is substituted"""
        for code, vote in ((397, 8.0), (220, 0.0), (356, 0.0)):
            player = Player.get_by_code(code)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 68)

    def test_two_substitutions_with_same_role(self):
        """Check if 2 non-evaluated players are substituted"""
        for code, vote in ((356, 0.0), (415, 0.0),
            (397, 8.0), (220, 7.0)):
            player = Player.get_by_code(code)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 69)

    def test_three_substitutions_with_same_role(self):
        """Check if 3 non-evaluated players are substituted"""
        for code, vote in ((356, 0.0), (415, 0.0), (510, 0.0),
            (397, 8.0), (220, 4.0), (584, 5.0)):
            player = Player.get_by_code(code)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 65)

    def test_four_substitutions_with_same_role(self):
        """Check if 4 non-evaluated players are substituted by only 3 ones"""
        for code, vote in ((356, 0.0), (415, 0.0), (510, 0.0), (971, 0.0),
            (397, 8.0), (220, 4.0), (584, 5.0), (914, 0.0)):
            player = Player.get_by_code(code)
            ev = Evaluation.objects.filter(player=player).first()
            ev.fanta_value = vote
            ev.save()
        self.assertEqual(self.handler.get_pts(), 59)
