from fantalega.models import Evaluation, Player


class LineupHandler(object):

    def __init__(self, lineup):
        self.lineup = lineup
        self.holders = [p for p in self.lineup.players.all()[:11]]
        self.substitutes = [p for p in self.lineup.players.all()[11:]]
        self.not_evaluated = []
        self.available_by_role = []
        self.added_player = []
        self.substitutions = 0
        self.candidate = None
        self.available = [p for p in self.substitutes
            if Evaluation.objects.filter(player=p, day=self.lineup.day
                ).first().fanta_value > 0.0 and p.role != 'goalkeeper']

    def get_goalkeeper_substitute(self):
        gks = [p for p in self.substitutes if Evaluation.objects.filter(
               player=p, day=self.lineup.day).first().fanta_value > 0.0 and
               p.role == 'goalkeeper']
        if gks:
            return gks[0]
        else:
            return None

    def get_evaluation(self, player):
        evaluation = Evaluation.objects.filter(player=player,
                                               day=self.lineup.day).first()
        return evaluation.fanta_value

    def need_substitutions(self):
        evaluated = [p for p in self.holders if self.get_evaluation(p) > 0.0]
        return len(evaluated) != 11

    def get_same_role_substitute(self, player):
        self.available_by_role = [p for p in self.substitutes
            if p.role == player.role and Evaluation.objects.filter(
                player=p, day=self.lineup.day).first().fanta_value > 0.0]
        self.candidate = self.available_by_role[0]
        return self.candidate

    def get_substitute(self, player):
        if player.role == 'goalkeeper':
            self.candidate = self.get_goalkeeper_substitute()
        else:
            #print self.available
            if self.available:
                return self.available[0]

    def is_same_role_available(self, player):
        self.available_by_role = [p for p in self.substitutes
            if p.role == player.role and Evaluation.objects.filter(
                player=p, day=self.lineup.day).first().fanta_value > 0.0]
        return len(self.available_by_role) > 0

    def is_substitute_available(self, player):
        self.available = [p for p in self.substitutes
            if Evaluation.objects.filter(player=p, day=self.lineup.day
                ).first().fanta_value > 0.0 and p.role != 'goalkeeper']
        return len(self.available) > 0

    def get_pts(self):
        if not self.need_substitutions():
            return sum([self.get_evaluation(p) for p in self.holders])
        else:
            self.not_evaluated = \
                [p for p in self.holders if Evaluation.objects.filter(
                    player=p, day=self.lineup.day).first().fanta_value == 0.0]
        for player in self.not_evaluated:
            if self.is_same_role_available(player):
                self.candidate = self.get_same_role_substitute(player)
                self.substitutes.pop(self.substitutes.index(self.candidate))
            elif self.is_substitute_available(player):
                self.candidate = self.get_substitute(player)
                ##check module##
                if self.is_module_accepted(player):
                    self.substitutes.pop(self.substitutes.index(self.candidate))
                else:
                    print "module doesn't exist!"
            else:
                self.candidate = None

            if self.candidate and self.substitutions < 3:
                self.added_player.append(self.candidate)
                self.substitutions += 1

        new_list = [p for p in self.holders if Evaluation.objects.filter(
            player=p, day=self.lineup.day).first().fanta_value > 0.0] +\
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
        return module in ('343', '352', '442', '433', '451', '532', '541')
