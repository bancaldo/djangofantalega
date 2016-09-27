from copy import copy
from random import shuffle


def first_step_season(teams):
    """
    first_step_season(teams) -> list
    create a matrix to fill with teams"""
    matrix = []
    counter = 0
    while counter < len(teams):
        matrix.append([None] * len(teams))
        counter += 1
    matrix[0] = teams  # header

    # reversed header without th last team
    row2 = copy(teams)
    row2.pop()
    row2.reverse()
    matrix[1][0:(len(teams) - 1)] = row2[0:(len(teams) - 1)]

    # Table composition: first step
    i = 1
    while i < len(teams):
        k = 1
        for item in matrix[i]:
            try:
                matrix[i + 1][k] = item
                matrix[i + 1][0] = matrix[i + 1][(len(teams) - 1)]
                matrix[i + 1][(len(teams) - 1)] = None
                k += 1
            except IndexError:
                break
        i += 1

    # Table composition: second step
    row_m = 1
    while row_m < len(teams):
        for item_a in matrix[0]:
            for item_b in matrix[row_m]:
                if matrix[0].index(item_a) == matrix[row_m].index(item_b):
                    if item_a == item_b:
                        matrix[row_m][matrix[row_m].index(item_b)] = \
                            teams[-1]
                        matrix[row_m][(len(teams) - 1)] = item_b
        row_m += 1

    cal = []
    day = 1
    while day < len(teams):
        first_round = []
        for team1 in matrix[0]:
            for team2 in matrix[day]:
                if matrix[0].index(team1) == matrix[day].index(team2):
                    if team2 not in first_round or team1 not in first_round:
                        if team1.home is True:
                            first_round.append(team1)
                            first_round.append(team2)
                            cal.append((day, team1, team2))
                            team1.set_visit()
                            team2.set_home()
                        else:
                            first_round.append(team2)
                            first_round.append(team1)
                            cal.append((day, team2, team1))
                            team1.set_home()
                            team2.set_visit()
        day += 1
    return cal


def second_step_season(cal, teams):
    """
    second_step_season(cal, teams) -> list

    Create the second round for season
    """
    scond_round_cal = []
    for match in cal:
        n, team1, team2 = match
        scond_round_cal.append((int(n) + len(teams) - 1, team2, team1))
    return scond_round_cal


def create_season(teams, num):
    """
    create_season(teams, num) -> list
    
    Iterable is the list of teams present in db
    num is the number of round of the tournament
    """
    shuffle(teams)
    for team in teams:
        team.home = True  # Init for home_visit team calculation
    cal = first_step_season(teams)
    rounds = 1
    full_cal = cal
    while rounds < num:
        cal = second_step_season(cal, teams)
        full_cal += cal
        rounds += 1
    return full_cal