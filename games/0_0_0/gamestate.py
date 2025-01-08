import os, sys 
from game_executables import *
from state.state import *
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from game_config import *
from game_executables import *
from game_calculations import * 

class GameState(GameExecutables):
    
    def runSpin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.resetBook()

            #Draw random board and 
            self.createBoardFromReelStrips()
            revealBoardEvent(self)

            #Modify board/apply special conditions

            #Evaluate wins
            self.calculateWins(winType="lineWins")
            winInfoEvent(self)

            #Check free-spin trigger
            if self.checkFreespinCondition():
                self.runFreeSpinFromBaseGame()

            #Verify win-criteria is satisfied
            self.record({"gameType":self.gameType,"book":self.bookId})

        self.imprintWins()
    
    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            self.createBoardFromReelStrips()
            revealBoardEvent(self)

            self.calculateWins(winType="lineWins")
            winInfoEvent(self)

            if self.checkFreespinCondition():
                self.updateFreeSpinRetriggerAmount()

    
    #TODO: create functions in better location, must be loaded in from Globals()
    def assignMultiplier(self, symbol:object):
        multValue = getRandomOutcome(self.getCurrentDistributionConditions()['multiplierValues'][self.gameType])
        symbol.assignAttribute({'multValue': multValue})
