# -*- coding: utf-8 -*-

class LineupHandler(object):

    def __init__(self, lineup_players):
        self.holders = lineup_players[:11]
        self.substitutes = lineup_players[11:]
        self.not_evaluated = []
        self.available = []
        self.available_by_role = []
        self.added_player = []
        self.substitutions = 0

    def check_holders(self):
        self.not_evaluated = [p for p in self.holders if p[2] == 0.0]

    def find_substitute(self):
        self.available = [p for p in self.substitutes if p[2] > 0.0]

    def is_same_role_available(self, player):
        return player[1] in [p[1] for p in self.available]

    def get_same_role_available(self, role):
        self.available_by_role = [p for p in
            self.available if p[1] == role]
        found = self.available_by_role.pop(0)
        self.available.pop(self.available.index(found))
        self.substitutions += 1
        return found

if __name__ == '__main__':
    players = [
        ('t1', 'p', 6.0), ('t2', 'd', 6.0), ('t3', 'd', 6.0),
        ('t4', 'd', 6.0), ('t5', 'c', 6.0), ('t6', 'c', 6.0),
        ('t7', 'c', 0.0), ('t8', 'c', 6.0), ('t9', 'a', 6.0),
        ('t10', 'a', 6.0), ('t11', 'a', 6.0), ('s1', 'p', 6.0),
        ('s2', 'd', 0.0), ('s3', 'd', 6.0), ('s4', 'd', 6.0),
        ('s5', 'c', 0.0), ('s6', 'c', 0.0), ('s7', 'c', 0.0),
        ('s8', 'a', 0.0), ('s9', 'a', 0.0), ('s10', 'a', 0.0),
        ]
    h = LineupHandler(players)
    #print h.holders
    #print h.substitutes
    h.check_holders()
    #print h.not_evaluated
    h.find_substitute()
    #print h.available
    for p in h.not_evaluated:
        print p
        if h.is_same_role_available(p) and h.substitutions < 3:
            h.added_player.append(h.get_same_role_available(p[1]))
            print h.added_player
            print h.available, h.substitutions
            #print h.available_by_role
        else:
            print "necessario cambio modulo" # cambio modulo
