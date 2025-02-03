import os, sys 
from game_override import *
from src.state.state import *
from src.events.events import set_total_event, set_win_event 
from game_config import *
from game_executables import *
from game_calculations import *

class GameState(GameStateOverride):

    def run_spin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.drawBoard()
            
            self.winData = self.getClusterWinData()
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            
            while self.winData['totalWin'] > 0 and not(self.wincap_triggered):
                self.winData = self.getClusterWinData()
                self.win_manager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
            
            self.set_end_tumble_event()
            
            self.win_manager.updateGameTypeWins(self.gametype)
            if self.check_fs_condition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.totFs:
            self.updateFreeSpin()
            self.drawBoard()
            #Apply game-specific actions (i.e special symbol attributes before or after evaluation)
            
            self.winData = self.getClusterWinData()
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            self.updateGridMultipliers()

            while self.winData['totalWin'] > 0 and not(self.wincap_triggered):
                self.winData = self.getClusterWinData()
                self.win_manager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
                self.updateGridMultipliers()
            
            self.set_end_tumble_event()
            self.win_manager.updateGameTypeWins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

    #Make a game which has multipliers on the wilds (like juice monster)
    #Mining game clone for scattery-pays (can also have symbol mults?)