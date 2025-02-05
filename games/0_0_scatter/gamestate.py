import os, sys
from game_override import *
from src.state.state import *
from game_config import *
from game_executables import *
from game_calculations import *
from src.events.events import freespin_end_event, tumble_board_event

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())


class GameState(GameStateOverride):

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            self.win_data = self.get_scatterpay_wins(record_wins=True)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            self.emit_tumble_events()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.win_data = self.get_scatterpay_wins(record_wins=True)
                self.win_manager.update_spinwin(self.win_data["totalWin"])
                self.emit_tumble_events()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            # Resets global multiplier at each spin
            self.update_freespin()
            self.draw_board()

            self.win_data = self.get_scatterpay_wins(record_wins=True)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            self.emit_tumble_events(tumble_after_wins=False)
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.update_global_mult()  # Special mechanic - increase multiplier with every tumble
                if len(self.book["events"]) == 48:
                    print("here")
                self.tumble_board()
                tumble_board_event(self)
                self.win_data = self.get_scatterpay_wins()
                self.win_manager.update_spinwin(self.win_data["totalWin"])
                self.emit_tumble_events(tumble_after_wins=False)

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
