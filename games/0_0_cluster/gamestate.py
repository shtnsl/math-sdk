import os, sys 
from game_override import *
from src.state.state import *
from src.events.events import setTotalWinEvent, setWinEvent 
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
            
            self.winData = self.getClusterWinData()
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            
            while self.winData['totalWin'] > 0 and not(self.winCapTriggered):
                self.winData = self.getClusterWinData()
                self.winManager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
            
            self.setEndOfTumbleWins()
            
            self.winManager.updateGameTypeWins(self.gameType)
            if self.checkFreespinCondition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluate_final_win()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            self.update_free_spin()
            self.drawBoard()
            #Apply game-specific actions (i.e special symbol attributes before or after evaluation)
            
            self.winData = self.getClusterWinData()
            self.winManager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            self.updateGridMultipliers()

            while self.winData['totalWin'] > 0 and not(self.winCapTriggered):
                self.winData = self.getClusterWinData()
                self.winManager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
                self.updateGridMultipliers()
            
            self.setEndOfTumbleWins()
            self.winManager.updateGameTypeWins(self.gameType)

            if self.checkFreespinCondition():
                self.update_free_spin_retrigger_amount()

    #Make a game which has multipliers on the wilds (like juice monster)
    #Mining game clone for scattery-pays (can also have symbol mults?)