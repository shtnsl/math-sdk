from game_executables import *
from calculations.statistics import getRandomOutcome

class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset 
    """

    def resetBook(self):
        #Reset global values used across multiple projects
        super().resetBook()
        #Reset parameters relevant to local game only

    def assignSpecialSymbolFuncions(self):
            specialSymbolFunctions = {
                'W': [self.assignMultiplierProperty],
                'M': [self.assignMultiplierProperty]
            }
            for name, symObject in self.validSymbols.items():
                if name in specialSymbolFunctions:
                    for func in specialSymbolFunctions[name]:
                        symObject.registerSpecialFunction(func)

    def assignWildProperty(self, symbol):
        symbol.wild = True
        # symbol.assignAttribute(attributeDict={'wild', True})

    def assignMultiplierProperty(self, symbol):
        multiplierValue = getRandomOutcome(self.getCurrentDistributionConditions()["multiplierValues"][self.gameType])
        symbol.multiplier = multiplierValue
        # symbol.assignAttribute(attributeDict={'multiplier': multiplierValue})