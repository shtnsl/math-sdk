from game_calculations import GameCalculations
from game_events import updateGridMultiplierEvent

class GameExecutables(GameCalculations):

    def resetGridMultipliers(self):
        self.positionMultipliers = [[1 for _ in range(self.config.numRows[reel])] for reel in range(self.config.numReels)]

    def updateGridMultipliers(self):
        if self.winData['totalWin'] > 0:
            for win in self.winData['wins']:
                for pos in win['positions']:
                    self.positionMultipliers[pos['reel']][pos['row']] *= 2
            updateGridMultiplierEvent(self)





























