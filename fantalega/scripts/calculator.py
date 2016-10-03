from fantalega.models import Evaluation


class BadInputError(Exception):
    pass


def _convert_pts_to_goals(pts):
    """
    _convert_pts_to_goals(pts) -> int

    Calculate number of goals by total pts, e.g.:
    _convert_pts_to_goals(60) -> 0
    _convert_pts_to_goals(66) -> 1
    _convert_pts_to_goals(72) -> 2

    :param pts: str lineup pts
    """
    if isinstance(pts, float):
        return (float(pts) - 60) // 6
    else:
        raise BadInputError("Need a Float as input")


def get_final(pts_a, pts_b):
    """
    get_final(pts_a, pts_b) -> tuple

    Convert pts to goals between 2 teams, e.g.:
    get_final(66, 62) -> (1, 0)

    :param pts_a: int pts of team A
    :param pts_b: int pts of team B
    """
    goal_a, goal_b = _convert_pts_to_goals(pts_a), _convert_pts_to_goals(pts_b)
    if goal_a == goal_b:
        if pts_a - pts_b >= 4:  # +4 in the same level results in +1 goal
            goal_a += 1
        elif pts_b - pts_a >= 4:  # +4 in the same level for team_b
            goal_b += 1
    if pts_a < 60:  # og for team_a
        goal_a = 0
        goal_b += 1
    elif pts_b < 60:  # og for team_b
        goal_b = 0
        goal_a += 1
    if pts_a - pts_b > 9.5:  # +10 in the same level results in +1 goal
        goal_a += 1
    elif pts_b - pts_a > 9.5:  # +10 for team_b
        goal_b += 1
    return int(goal_a), int(goal_b)


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
    data = {'hw': 0, 'hm': 0, 'hl': 0, 'hgm': goals_a, 'hgc':goals_b,
            'vw': 0, 'vm': 0, 'vl': 0, 'vgm': goals_b, 'vgc':goals_a}
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
    """Handler for lineup players evauations"""
    def __init__(self, lineup, day, offset=0):
        """
        Calculator(lineup, day, offset)

        Calculate the lineup pts handling substitutions

        :param lineup: LineUp object
        :param day: int day
        :param offset: int difference between league day and real day
        """
        self.offset = offset
        self.lineup = lineup
        self.holders = self.lineup.players.all()[:11]
        self.substitutes = self.lineup.players.all()[11:]
        self.day = int(day) + self.offset
        self.evaluated = []
        self.not_evaluated = []
        self.evaluated_subs = []
        self.chosen = []
        self.iterable = []
        self.pts = 0.0
        self.holders_total = 0.0

    def calc_holders_total(self):
        self.holders_total = 0.0
        self.evaluated = []
        self.not_evaluated = []
        for player in self.holders:
            evaluation = Evaluation.objects.filter(player=player,
                                        day=self.day).first()
            # print "%s -> %s" % (player.name, evaluation.fanta_value)
            self.holders_total += evaluation.fanta_value
            if not evaluation.fanta_value == 0.0:
                self.evaluated.append((player, evaluation))
            else:
                self.not_evaluated.append(player)
        return self.holders_total

    def get_same_role_subs(self, role):
        availables = [p for p in self.substitutes if p.role == role]
        for player in availables:
            print player
            fv = Evaluation.objects.filter(player=player, day=self.day).first()
            print fv.fanta_value
            if fv.fanta_value > 0.0:
                self.chosen.append((player, fv))
        return None, None

    def calculate_pts(self):
        """calculate_pts(self) -> res, dict"""
        res = 0
        self.evaluated = []
        self.not_evaluated = []
        for player in self.holders:
            evaluation = Evaluation.objects.filter(player=player,
                                        day=self.day).first()
            if not evaluation.net_value == 0.0:
                self.evaluated.append((player, evaluation))
            else:
                self.not_evaluated.append(player)
        # if the evaluated players length is 11 (no substitutions), it returns
        # the fanta_values sum
        if len(self.evaluated) == 11:
            res = sum([v.fanta_value for p, v in self.evaluated])

        # SUBSTITUTE: substitutions check
        # if the player without evaluations are 3, the "check_for_substitutes"
        # methods are called, else the method "substitute_cyclic" is called.
        else:
            if len(self.not_evaluated) < 4:
                self.chosen = self._get_substitutes()
            else:
                self.chosen = self._get_substitutes_cyclic()
            self.evaluated += self.chosen
            res = sum([v.fanta_value for p, v in self.evaluated])
        self.pts = res
        dv = {item[0].name: item[1].fanta_value for item in self.evaluated}
        return res, dv




    def _filter_evaluated_subs(self):
        """
        _filter_evaluated_subs(self) -> list of Player objects

        Filter the substitutes and extract the evaluated ones

        :return: list of Player objects
        """
        evaluated_subs = []
        for substitute in self.substitutes:
            evaluation = Evaluation.objects.filter(player=substitute,
                                    day=self.day).first()
            if evaluation.fanta_value > 0.0:
                evaluated_subs.append((substitute, evaluation))
        return evaluated_subs

    def _get_substitutes(self):
        """
        _get_substitutes(self) -> list di object Player

        Get substitutes, if possible, between the evaluated substitutes,
        if the holders player is not evaluated and the substitutions to do are 3.

        :return self.chosen: list of Player objects
        """
        self.evaluated_subs = self._filter_evaluated_subs()

        for not_evaluated_player in self.not_evaluated:
            if 200 < not_evaluated_player.code < 500:
                available = self._search_defender()
                if available:
                    self.chosen.append(self.evaluated_subs.pop(
                        self.evaluated_subs.index(available)))
            elif 500 < not_evaluated_player.code < 800:
                available = self._search_midfielder()
                if available:
                    self.chosen.append(self.evaluated_subs.pop(
                        self.evaluated_subs.index(available)))
            elif not_evaluated_player.code > 800:
                available = self._search_forwards()
                if available:
                    self.chosen.append(self.evaluated_subs.pop(
                        self.evaluated_subs.index(available)))
            else:
                available = self._search_goalkeeper()
                if available:
                    self.chosen.append(self.evaluated_subs.pop(
                        self.evaluated_subs.index(available)))
        return self.chosen

    def _get_substitutes_cyclic(self):
        """
        _get_substitutes_cyclic(self) -> list di object Player

        If there is more than 3 substitutions. it loops over the available
        substitutes to cover every role before get 2 substitutes of the same
        role.

        :return chosen: list of Player objects
        """
        self.evaluated_subs = self._filter_evaluated_subs()
        chosen = []
        substitutes = []
        goalkeepers = False
        dfs = False
        mfs = False
        fws = False
        while True:
            for not_evaluated_player in self.not_evaluated:
                if 200 < not_evaluated_player.code < 500:
                    available = self._search_defender()
                    if dfs is False:
                        chosen.append(self.evaluated_subs.pop(
                            self.evaluated_subs.index(available)))
                        substitutes.append(self.not_evaluated.pop(
                            self.not_evaluated.index(not_evaluated_player)))
                        dfs = True
                        goalkeepers = False
                        mfs = False
                        fws = False
                elif 500 < not_evaluated_player.code < 800:
                    available = self._search_midfielder()
                    if mfs is False:
                        chosen.append(self.evaluated_subs.pop(
                            self.evaluated_subs.index(available)))
                        substitutes.append(self.not_evaluated.pop(
                            self.not_evaluated.index(not_evaluated_player)))
                        mfs = True
                        goalkeepers = False
                        dfs = False
                        fws = False
                elif not_evaluated_player.code > 800:
                    available = self._search_forwards()
                    if fws is False:
                        chosen.append(self.evaluated_subs.pop(
                            self.evaluated_subs.index(available)))
                        substitutes.append(self.not_evaluated.pop(
                            self.not_evaluated.index(not_evaluated_player)))
                        fws = True
                        goalkeepers = False
                        dfs = False
                        mfs = False
                else:
                    available = self._search_goalkeeper()
                    if goalkeepers is False:
                        chosen.append(self.evaluated_subs.pop(
                            self.evaluated_subs.index(available)))
                        substitutes.append(self.not_evaluated.pop(
                            self.not_evaluated.index(not_evaluated_player)))
                        goalkeepers = True
                        fws = False
                        dfs = False
                        mfs = False

            if len(chosen) == 3:
                return chosen
        return chosen

    def _search_defender(self):
        """
        _search_defender(self) -> object Player

        Search for a defender substitute

        :return: object Player
        """
        defenders = [(defender, ev) for defender, ev in self.evaluated_subs
                     if 200 < defender.code < 500]
        if defenders:
            return defenders[0]

    def _search_midfielder(self):
        """
        _search_midfielder(self) -> object Player

        Search for a midfielder substitute

        :return: object Player
        """
        midfielders = [(mid, ev) for mid, ev in self.evaluated_subs
                       if 500 < mid.code < 800]
        if midfielders:
            return midfielders[0]

    def _search_forwards(self):
        """
        _search_forwards(self) -> object Player

        Search for a forwards substitute

        :return: object Player
        """
        forwards = [(forward, ev) for forward, ev in self.evaluated_subs
                    if forward.code > 800]
        if forwards:
            return forwards[0]

    def _search_goalkeeper(self):
        """
        _search_goalkeeper(self) -> object Player

        Search for a goalkeeper substitute

        :return: object Player
        """
        goalkeepers = [(goalkeeper, ev) for goalkeeper, ev in
                       self.evaluated_subs if goalkeeper.code < 200]
        if goalkeepers:
            return goalkeepers[0]

    def get_pts(self):
        """
        get_pts(self) -> int
        """
        self.calculate_pts()
        return self.pts


def pts_calculator(lineup, day, offset):
    lh = LineupHandler(lineup, day, offset)
    lh.calc_holders_total()
    for p in lh.not_evaluated:
        lh.get_same_role_subs(p.role)
    evaluated_lineup = lh.evaluated + lh.chosen
    total = sum([ev.fanta_value for player, ev in evaluated_lineup])
    return total

