import os, sys 
from game_override import *
from src.state.state import *
from src.events.events import set_total_event, set_win_event
from game_config import *
from game_executables import *
from game_calculations import *

class GameState(GameStateOverride):

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()
            
            self.win_data = self.get_cluster_data()
            self.win_manager.update_spinwin(self.win_data['totalWin'])
            self.emit_tumble_events()
            
            while self.win_data['totalWin'] > 0 and not(self.wincap_triggered):
                self.win_data = self.get_cluster_data()
                self.win_manager.update_spinwin(self.win_data['totalWin'])
                self.emit_tumble_events()
            
            self.set_end_tumble_event()
            
            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            #Apply game-specific actions (i.e special symbol attributes before or after evaluation)
            
            self.win_data = self.get_cluster_data()
            self.win_manager.update_spinwin(self.win_data['totalWin'])
            self.emit_tumble_events()
            self.update_grid_mults()

            while self.win_data['totalWin'] > 0 and not(self.wincap_triggered):
                self.win_data = self.get_cluster_data()
                self.win_manager.update_spinwin(self.win_data['totalWin'])
                self.emit_tumble_events()
                self.update_grid_mults()
            
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()