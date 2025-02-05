from copy import copy
from src.events.events import set_win_event, set_total_event
from src.calculations.board import Board


class Tumble(Board):
    """General class for cascading/tumble game actions."""

    def tumble_board(self) -> None:
        """Remove winning symbols from the active gameboard."""
        self.tumbles += 1
        self.board_before_tumble = copy(self.board)
        static_board = copy(self.board)
        self.new_symbols_from_tumble = [[] for _ in range(len(static_board))]

        for reel, _ in enumerate(static_board):
            exploding_symbols = 0
            copy_reel = static_board[reel]
            for row in range(len(static_board[reel])):
                if static_board[reel][-1 - row].check_attribute("explode"):
                    exploding_symbols += 1

            for i in range(exploding_symbols):
                reel_pos = (self.reel_positions[reel] - 1) % len(self.reelstrip[reel])
                self.reel_positions[reel] = reel_pos
                if i == 0 and self.config.include_padding:
                    insert_sym = self.top_symbols[reel]
                else:
                    nme = self.reelstrip[reel][(reel_pos) % len(self.reelstrip[reel])]
                    insert_sym = self.create_symbol(nme)
                copy_reel.insert(0, insert_sym)
                self.new_symbols_from_tumble[reel].append(insert_sym)

            copy_reel = [copy(sym) for sym in copy_reel if not sym.check_attribute("explode")]
            if len(copy_reel) != self.config.num_rows[reel]:
                raise RuntimeError(
                    f"new reel length must match expected board size:\n expected: {self.config.num_rows[reel]} \n actual: {len(copy_reel)}"
                )
            static_board[reel] = copy_reel

        # update topSymbol positions
        if self.config.include_padding:
            self.top_symbols = [[] for _ in range(self.config.num_reels)]
            for reel in range(self.config.num_reels):
                self.top_symbols[reel] = self.create_symbol(
                    str(self.reelstrip[reel][(self.reel_positions[reel] - 1) % len(self.reelstrip[reel])])
                )

        self.get_special_symbols_on_board()
        self.board = static_board

    def set_end_tumble_event(self) -> None:
        """Emit wins related to latest cumulative tumble sequence."""
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)
