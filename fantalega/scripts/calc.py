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
        raise BadInputError("Need a Float as input")


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
        raise BadInputError("Need a Float as input")


def lineups_data(goals_a, goals_b):
    """
    lineups_data(goals_a, goals_b) -> dict

    Convert to goals team data as: won, lost, matched, goals_made etc, i.e.:
    lineups_data(3, 2) -> {'hw': 1, 'vw': 0, 'hl': 0, ...}
    hw stays for home_won
    hm stays for home_matched
    hl stays for home_lost
    hgm stays for home goals made
    hgc stays for home goals conceded

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
    def __init__(self, lineup, day, offset):
        self.day = day + offset
        self.lineup = lineup
        self.holders = [p for p in self.lineup.players.all()[:11]]
        self.substitutes = [p for p in self.lineup.players.all()[11:]]
        self.not_evaluated = []
        self.available_by_role = []
        self.added_player = []
        self.substitutions = 0
        self.candidate = None
        self.available = [p for p in self.substitutes if
                          Evaluation.objects.filter(player=p, day=self.day
                                                    ).first().fanta_value > 0.0
                          and p.role != 'goalkeeper']

    def get_goalkeeper_substitute(self):
        gks = [p for p in self.substitutes if Evaluation.objects.filter(
               player=p, day=self.day).first().fanta_value > 0.0 and
               p.role == 'goalkeeper']
        if gks:
            return gks[0]
        else:
            return None

    def get_evaluation(self, player):
        evaluation = Evaluation.objects.filter(player=player,
                                               day=self.day).first()
        return evaluation.fanta_value

    def need_substitutions(self):
        evaluated = [p for p in self.holders if self.get_evaluation(p) > 0.0]
        return len(evaluated) != 11

    def get_same_role_substitute(self, player):
        self.available_by_role = [p for p in self.substitutes
                                  if p.role == player.role and
                                  Evaluation.objects.filter(
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
                                      player=p, day=self.day
                                  ).first().fanta_value > 0.0]
        return len(self.available_by_role) > 0

    def is_substitute_available(self):
        self.available = [p for p in self.substitutes if
                          Evaluation.objects.filter(
                              player=p, day=self.day
                          ).first().fanta_value > 0.0 and
                          p.role != 'goalkeeper']
        return len(self.available) > 0

    def get_pts(self):
        if not self.need_substitutions():
            return sum([self.get_evaluation(p) for p in self.holders])
        else:
            self.not_evaluated = \
                [p for p in self.holders if Evaluation.objects.filter(
                    player=p, day=self.day).first().fanta_value == 0.0]
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

        new_list = [p for p in self.holders if Evaluation.objects.filter(
            player=p, day=self.day).first().fanta_value > 0.0] +\
            self.added_player
        return sum([self.get_evaluation(p) for p in new_list])

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
