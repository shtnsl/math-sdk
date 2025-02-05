import os, sys
from game_override import *
from src.state.state import *
from src.events.events import (
    set_total_event,
    tumble_board_event,
    set_win_event,
    update_global_mult_event,
)

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from game_config import *
from game_executables import *
from game_calculations import *


class GameState(GameStateOverride):

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=True)

            self.win_data = self.getWaysWinData()
            self.win_manager.update_spinwin(self.win_data["totalWin"])

            self.evaluate_final_win()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
