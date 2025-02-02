from game_executables import *
from src.calculations.statistics import getRandomOutcome

class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset 
    """

    def resetBook(self):
        #Reset global values used across multiple projects
        super().resetBook()
        #Reset parameters relevant to local game only
        self.emitWinEvent = True
        self.cumulativePrize = 0

    def assignSpecialSymbolFunctions(self):
        self.specialSymbolFunctions = {
            'M': [self.assignMultiplierProperty],
            'W': [self.assignMultiplierProperty]
        }

    def assignMultiplierProperty(self, symbol):
        if self.gameType == self.config.freeGameType:
            multiplierValue = getRandomOutcome(self.getCurrentDistributionConditions()["multiplierValues"][self.gameType])
            symbol.assignAttribute({'multiplier': multiplierValue})
        elif self.gameType == self.config.baseGameType:
            symbol.assignAttribute({'multiplier': 1})

    
    def checkRepeat(self):
        super().checkRepeat()
        if self.repeat == False:
            winCriteria = self.getCurrentBetModeDistribution().getWinCriteria()
            if winCriteria is not None and self.finalWin != winCriteria:
                self.repeat = True 
                return 
            if winCriteria == None and self.finalWin == 0:
                self.repeat = True 
                return 
            
