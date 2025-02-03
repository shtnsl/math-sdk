import os, sys 
from game_override import *
from src.state.state import *
from game_config import *
from game_executables import *
from game_calculations import * 
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

class GameState(GameStateOverride):

    def run_spin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.drawBoard()

            self.winData = self.getScatterPayWinData(recordWins=True)
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()

            while self.winData['totalWin'] > 0 and not(self.wincap_triggered):
                self.winData = self.getScatterPayWinData(recordWins=True)
                self.win_manager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()

            self.set_end_tumble_event()
            self.win_manager.updateGameTypeWins(self.gametype)
            
            if self.check_fs_condition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.totFs:
            #Resets global multiplier at each spin
            self.updateFreeSpin()
            self.drawBoard()

            self.winData = self.getScatterPayWinData(recordWins=True)
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitTumbleWinEvents()
            while self.winData['totalWin'] > 0 and not(self.wincap_triggered):
                self.update_global_mult() #Special mechanic - increase multiplier with every tumble
                self.winData = self.getScatterPayWinData()
                self.win_manager.updateSpinWin(self.winData['totalWin'])
                self.emitTumbleWinEvents()
                
            self.set_end_tumble_event()
            self.win_manager.updateGameTypeWins(self.gametype)
    
            if self.check_fs_condition():
                self.update_fs_retrigger_amt()



