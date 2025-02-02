import os, sys 
from game_override import *
from src.state.state import *
from game_config import *
from game_executables import *
from game_calculations import * 
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

class GameState(GameStateOverride):

    def runSpin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.resetBook()
            self.drawBoard()

            self.winData = self.getScatterPayWinData(recordWins=True)
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()

            while self.winData['totalWin'] > 0 and not(self.winCapTriggered):
                self.winData = self.getScatterPayWinData(recordWins=True)
                self.winManager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()

            self.setEndOfTumbleWins()
            self.winManager.updateGameTypeWins(self.gameType)
            
            if self.checkFreespinCondition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()
            self.checkRepeat()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            #Resets global multiplier at each spin
            self.updateFreeSpin()
            self.drawBoard()

            self.winData = self.getScatterPayWinData(recordWins=True)
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            while self.winData['totalWin'] > 0 and not(self.winCapTriggered):
                self.updateGlobalMult() #Special mechanic - increase multiplier with every tumble
                self.winData = self.getScatterPayWinData()
                self.winManager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
                
            self.setEndOfTumbleWins()
            self.winManager.updateGameTypeWins(self.gameType)
    
            if self.checkFreespinCondition():
                self.updateFreeSpinRetriggerAmount()



