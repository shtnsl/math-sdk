import sys
sys.path.append('./')
from src.executables.executables import Executables

class GameCalculations(Executables):

    def getBoardMultipliers(self, multiplerKey: str = "multiplier") -> list:
        boardMult = 0
        numMults = 0
        multInfo = []
        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                if self.board[reel][row].hasAttribute(multiplerKey):
                    boardMult += self.board[reel][row].multiplierKey
                    numMults += 1
                    multInfo.append({'reel': reel, 'row': row, 'value': self.board[reel][row].multiplierKey})
    
        return max(1, boardMult), multInfo