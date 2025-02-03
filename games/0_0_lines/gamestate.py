import os, sys 
from game_override import *
from src.state.state import *
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
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

            self.winData = self.getLineWinData(recordWins=True)
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitLineWinEvents()
            
            self.win_manager.updateGameTypeWins(self.gametype)
            if self.check_fs_condition():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()
            self.check_repeat()

        self.imprint_wins()
    
    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.totFs:
            self.updateFreeSpin()
            self.drawBoard()

            self.winData = self.getLineWinData(recordWins=True)
            self.win_manager.updateSpinWin(self.winData['totalWin'])
            self.emitLineWinEvents()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.updateGameTypeWins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

