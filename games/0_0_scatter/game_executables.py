from game_calculations import GameCalculations
from src.events.events import (
    update_global_mult_event,
    tumeble_board_event,
    win_info_event,
    set_win_event,
    set_total_event,
    fs_trigger_event,
)
from game_events import update_tunble_win_event, send_mult_info_event
from copy import copy


class GameExecutables(GameCalculations):

    def set_end_tumble_event(self):
        if self.gametype == self.config.freegame_type:  # Only multipliers in freeSpins
            board_mult, mult_info = self.get_board_multipliers()
            baseTumbleWin = copy(self.win_manager.spin_win)
            self.win_manager.set_spin_win(baseTumbleWin * board_mult)
            if self.win_manager.spin_win > 0 and len(mult_info) > 0:
                send_mult_info_event(
                    self,
                    board_mult,
                    mult_info,
                    baseTumbleWin,
                    self.win_manager.spin_win,
                )
                update_tunble_win_event(self)

        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def update_global_mult(self):
        self.global_multiplier += 1
        update_global_mult_event(self)

    def update_freespin_amount(self, scatterKey: str = "scatter"):
        self.tot_fs = self.count_special_symbols(scatterKey) * 2
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(
            self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger
        )
