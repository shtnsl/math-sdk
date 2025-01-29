import os, sys 
from state_override import *
from src.state.state import *
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from game_config import *
from game_executables import *
from game_calculations import * 

class GameState(GameStateOverride):

    def runSpin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.resetBook()
            self.drawBoard()

            self.winData = self.getLineWinData(recordWins=True)
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitLineWinEvents()
            
            self.winManager.updateGameTypeWins(self.gameType)
            if self.checkFreespinCondition():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()
            self.checkRepeat()

        self.imprintWins()
    
    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            self.updateFreeSpin()
            self.drawBoard()

            self.winData = self.getLineWinData(recordWins=True)
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitLineWinEvents()

            if self.checkFreespinCondition():
                self.updateFreeSpinRetriggerAmount()

            self.winManager.updateGameTypeWins(self.gameType)
        #send freeSpinEnd event
