from fantalega.models import Evaluation


class BadInputError(Exception):
    pass


def convert_pts_to_goals(pts):
    """
    convert_pts_to_goals(pts) -> int

    Calculate number of goals by total pts, e.g.:
    convert_pts_to_goals(60) -> 0
    convert_pts_to_goals(66) -> 1
    convert_pts_to_goals(72) -> 2
    """
    if isinstance(pts, float):
        if pts < 60.0:
            return 0
        return (float(pts) - 60) // 6
    else:
        raise BadInputError("Need a Float as input, %s in input" % pts)


def get_final(pts_a, pts_b):
    """
    get_final(pts_a, pts_b) -> tuple

    Convert pts to goals between 2 teams, e.g.:
    get_final(66, 62) -> (1, 0)
    """
    if isinstance(pts_a, float) and isinstance(pts_b, float):
        goal_a = convert_pts_to_goals(pts_a)
        goal_b = convert_pts_to_goals(pts_b)
        if goal_a == goal_b:
            if pts_a - pts_b >= 4:  # +4 in the same level results in +1 goal
                goal_a += 1
            elif pts_b - pts_a >= 4:  # +4 in the same level for team_b
                goal_b += 1
        if pts_a < 60:  # og for team_a
            goal_b += 1
        if pts_b < 60:  # og for team_b
            goal_a += 1
        if pts_a - pts_b > 9.5:  # +10 in the same level results in +1 goal
            goal_a += 1
        elif pts_b - pts_a > 9.5:  # +10 for team_b
            goal_b += 1
        return int(goal_a), int(goal_b)
    else:
        raise BadInputError("Need a Float as input, %s and %s in input" %\
                            (pts_a, pts_b))


def lineups_data(goals_a, goals_b):
    """
    lineups_data(goals_a, goals_b) -> dict

    Convert to goals team data as: won, lost, matched, goals_made etc, i.e.:
    lineups_data(3, 2) -> {'hw': 1, 'vw': 0, 'hl': 0, ...}
    hw: home_won               vw: visit_won
    hm: home_matched           vm: visit_matched
    hl: home_lost              ...and so on
    hgm: home goals made
    hgc: home goals conceded

    :param goals_a: int goals of team A
    :param goals_b: int goals of team B
    """
    data = {'hw': 0, 'hm': 0, 'hl': 0, 'hgm': goals_a, 'hgc': goals_b,
            'vw': 0, 'vm': 0, 'vl': 0, 'vgm': goals_b, 'vgc': goals_a}
    if goals_a > goals_b:
        data['hw'] = 1
        data['hl'] = 0
        data['hm'] = 0
        data['vw'] = 0
        data['vl'] = 1
        data['vm'] = 0
    elif goals_a < goals_b:
        data['hw'] = 0
        data['hl'] = 1
        data['hm'] = 0
        data['vw'] = 1
        data['vl'] = 0
        data['vm'] = 0
    else:
        data['hw'] = 0
        data['hl'] = 0
        data['hm'] = 1
        data['vw'] = 0
        data['vl'] = 0
        data['vm'] = 1
    return data


class LineupHandler(object):
    def __init__(self, lineup, day, league):
        self.league = league
        self.day = day + league.offset
        self.mod = 0.0
        self.lineup = lineup
        self.holders = [p for p in self.lineup.players.all()[:11]]
        self.substitutes = [p for p in self.lineup.players.all()[11:]]
        self.not_evaluated = []
        self.available_by_role = []
        self.added_player = []
        self.new_list = []
        self.substitutions = 0
        self.candidate = None
        self.available = [p for p in self.substitutes if
                          Evaluation.objects.filter(player=p, day=self.day,
                                                    season=league.season
                                                    ).first().fanta_value > 0.0
                          and p.role != 'goalkeeper']

    def get_goalkeeper_substitute(self):
        gks = [p for p in self.substitutes if Evaluation.objects.filter(
               player=p, day=self.day, season=self.league.season
               ).first().fanta_value > 0.0
               and p.role == 'goalkeeper']
        if gks:
            return gks[0]
        else:
            return None

    def get_evaluation(self, player):
        evaluation = Evaluation.objects.filter(player=player,
                                               season=self.league.season,
                                               day=self.day).first()
        return evaluation.fanta_value

    def need_substitutions(self):
        evaluated = [p for p in self.holders if self.get_evaluation(p) > 0.0]
        return len(evaluated) != 11

    def get_same_role_substitute(self, player):
        self.available_by_role = [p for p in self.substitutes
                                  if p.role == player.role and
                                  Evaluation.objects.filter(
                                      season=self.league.season,
                                      player=p, day=self.day
                                  ).first().fanta_value > 0.0]
        self.candidate = self.available_by_role[0]
        return self.candidate

    def get_substitute(self, player):
        if player.role == 'goalkeeper':
            self.candidate = self.get_goalkeeper_substitute()
        else:
            # print self.available
            if self.available:
                return self.available[0]

    def is_same_role_available(self, player):
        self.available_by_role = [p for p in self.substitutes if
                                  p.role == player.role and
                                  Evaluation.objects.filter(
                                      season=self.league.season,
                                      player=p, day=self.day
                                  ).first().fanta_value > 0.0]
        return len(self.available_by_role) > 0

    def is_substitute_available(self):
        self.available = [p for p in self.substitutes if
                          Evaluation.objects.filter(
                              season=self.league.season,
                              player=p, day=self.day
                          ).first().fanta_value > 0.0 and
                          p.role != 'goalkeeper']
        return len(self.available) > 0

    def get_pts(self):
        if not self.need_substitutions():
            return self.def_mod(self.holders)
        else:
            self.not_evaluated = \
                [p for p in self.holders if Evaluation.objects.filter(
                    player=p, day=self.day, season=self.league.season
                ).first().fanta_value == 0.0]
        for player in self.not_evaluated:
            if self.is_same_role_available(player):
                self.candidate = self.get_same_role_substitute(player)
                self.substitutes.pop(self.substitutes.index(self.candidate))
            elif self.is_substitute_available():
                self.candidate = self.get_substitute(player)
                # check module
                if self.is_module_accepted(player):
                    self.substitutes.pop(self.substitutes.index(self.candidate))
                else:
                    print "\n[WARNING] module doesn't exist!"
                    self.candidate = None
            else:
                self.candidate = None

            if self.candidate and self.substitutions < 3:
                self.added_player.append(self.candidate)
                self.substitutions += 1

        self.new_list = [p for p in self.holders if Evaluation.objects.filter(
            player=p, day=self.day, season=self.league.season
            ).first().fanta_value > 0.0] +\
            self.added_player
        return self.def_mod(self.new_list)

    def is_module_accepted(self, player):
        d, m, f = 0, 0, 0
        lineup = self.holders[:]
        lineup.pop(lineup.index(player))
        lineup.append(self.candidate)
        for role in [p.role for p in lineup]:
            if role == 'defender':
                d += 1
            elif role == 'midfielder':
                m += 1
            elif role == 'forward':
                f += 1
            else:
                pass
        module = '%s%s%s' % (d, m, f)
        print "\n[INFO] module changes in %s" % module
        return module in ('343', '352', '442', '433', '451', '532', '541')

    def def_mod(self, player_list):
        total = sum([Evaluation.objects.filter(
            player=p, day=self.day, season=self.league.season
            ).first().fanta_value for p in player_list])
        defenders = [p for p in player_list if p.role == 'defender']
        goalkeepers = [p for p in player_list if p.role == 'goalkeeper']
        gk = goalkeepers[0] if goalkeepers else None
        vgk = Evaluation.objects.filter(player=gk, day=self.day,
                                        season=self.league.season
                                        ).first().net_value
        def_votes = [Evaluation.objects.filter(season=self.league.season,
            player=d, day=self.day).first().net_value for d in defenders]
        if len(defenders) >= 4 and gk:
            if vgk == 0.0:
                vgk = 6.0
            for v in def_votes:
                if v == 0.0:
                    def_votes[def_votes.index(v)] = 6.0
            values = sorted(def_votes, reverse=True)[:3] + [vgk]
            avg_def = sum(values)/4.0
            if avg_def == 6:
                self.mod = 1
            elif 6 < avg_def <= 6.25:
                self.mod = 2
            elif 6.25 < avg_def <= 6.5:
                self.mod = 3
            elif 6.5 < avg_def <= 6.75:
                self.mod = 4
            elif 6.75 < avg_def <= 7:
                self.mod = 5
            elif avg_def > 7:
                self.mod = 6
            return total + self.mod
        else:
            return total
