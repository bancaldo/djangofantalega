import xlrd


class LineupExtractor(object):
    """This class is for development and debug only.
       It extracts a lineup from MCBEGxxxx.xls file.
       
       LineupExtractor(path, name, day)

       calling the extract method will return an iterable
       of the lineup players.
       e.g.
       >>> e = Extractor('MCBeg1617.xls', 'ME A SAN BULGNAIS', day=2)
       >>> players = e.extract()
    """
    def __init__(self, xls_file, name, day):
        self.workbook = xlrd.open_workbook(xls_file)
        self.sheets = self.workbook.sheets()
        self.sheet = self.workbook.sheet_by_index(2)
        self.rows = self.sheet.nrows
        self.players = []
        self.start_row = 0
        self.day = day
        self.name = name

    def get_start_row(self):
        """get_start_row(self) -> int

           return the row of day=day.
           from that row, the extractor starts to parse for team name
        """
        for row in range(self.sheet.nrows):
            try:
                string = str(self.sheet.cell_value(rowx=row, colx=0))
                if string.lower() == 'giornata':
                    xls_day = int(self.sheet.cell_value(rowx=row, colx=2))
                    if xls_day == self.day:
                        return row
            except ValueError:
                pass

    def get_team_row(self, home=True):
        """get_team_row(self) -> int

           return the row of team=name.
           if home=True it looks for team in home_team column
           else in visit_team one.
           from that row, the extractor starts to parse for players
        """
        for row in range(self.start_row, self.start_row + 121):
            if home:
                column = 0
            else:
                column = 4
            string = str(self.sheet.cell_value(rowx=row, colx=column))
            if string.lower() == self.name.lower():
                return row, column
        return None, None

    def extract(self):
        """extract(self) -> iterable

           return the list of lineup players filtered by team=name
           and day=day.
           First it looks for the day row, second it searches the
           team-list of players start row and then returns the list
           of player
        """
        self.start_row = self.get_start_row()
        row, column = self.get_team_row()
        if not row:
            row, column = self.get_team_row(home=False)
        if column == 0:
            c_players = 1
        else:
            c_players = 5
        for row in range(row + 2, row + 23):
            player = str(self.sheet.cell_value(rowx=row, colx=c_players))
            if not player:
                player = None
            self.players.append(player)
        return self.players
